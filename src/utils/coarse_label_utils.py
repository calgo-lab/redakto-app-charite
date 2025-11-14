from typing import Any, Dict, List, Set, Tuple

from pandas import DataFrame, Series

import re


class CoarseLabelUtils:
    """
    Utility class for handling entity annotations and merging consecutive entities and 
    measuring performance metrics.
    """

    @staticmethod
    def are_entities_consecutive_generic(current_entity: Series, 
                                         next_entity: Series, 
                                         input_text: str, 
                                         max_gap: int = 4) -> bool:
        """
        Check if two entities are consecutive with natural text separators:
        - (1) space, 
        - (2) comma, 
        - (3) dot, 
        - (4) hyphen, 
        - (5) colon, 
        - (6) semicolon, 
        - (7) parentheses, 
        - (8) square brackets, 
        - (9) curly braces,
        - (10) quotes,
        - (11) slashes,
        - (12) backslashes
        and combinations thereof, with a maximum gap of `max_gap` characters.
        
        :param current_entity: Series representing the current entity
        :param next_entity: Series representing the next entity
        :param input_text: the full text string containing the entities
        :param max_gap: maximum number of characters allowed between entities
        :return: True if entities are consecutive with allowed separators, False otherwise
        """
        if next_entity['Start'] < current_entity['End']:
            return False
        if next_entity['Start'] == current_entity['End']:
            return True

        between_text = input_text[current_entity['End']: next_entity['Start']]
        separator_pattern = r'^[\s,.\-:;()\[\]{}"\'/\\]*$'
        
        return re.match(separator_pattern, between_text) and len(between_text) <= max_gap

    @staticmethod
    def map_to_coarse_labels(annotation_df: DataFrame, 
                             input_text: str, 
                             fine_to_coarse_mapping: Dict[str, str], 
                             skip_labels: Set[str] = set(), 
                             merge_consecutive: bool = False) -> Tuple[DataFrame, Dict]:
        """
        Map entities to coarse labels while preserving original information,
        then merge consecutive entities of the same coarse type.
        
        :param fine_to_coarse_mapping: dict mapping fine-grained labels to coarse labels
        :param skip_labels: set of labels to skip during mapping
        :param annotation_df: DataFrame with columns ['Token_ID', 'Label', 'Start', 'End', 'Token']
        :param input_text: the full text string containing the entities
        :param merge_consecutive: whether to merge consecutive entities of the same coarse type
        :return: Tuple of (final DataFrame, tracking dictionary)
        """
        if annotation_df.empty:
            return annotation_df, dict()

        annotation_df = annotation_df[annotation_df['Start'] != -1].copy()
        if annotation_df.empty:
            return annotation_df, dict()
        
        if skip_labels:
            annotation_df = annotation_df[~annotation_df['Label'].isin(skip_labels)]
            if annotation_df.empty:
                return annotation_df, dict()

        mapped_df: DataFrame = annotation_df.copy().sort_values('Start').reset_index(drop=True)
        entity_tracking: Dict[str, Dict[str, Any]] = dict()
        
        for idx, row in mapped_df.iterrows():
            fine_label: str = row['Label']
            coarse_label: str = fine_to_coarse_mapping.get(fine_label, fine_label)

            entity_id: str = row['Token_ID']
            entity_tracking[entity_id] = {
                'original_label': fine_label,
                'original_token': row['Token'],
                'start': row['Start'],
                'end': row['End'],
                'coarse_label': coarse_label
            }
            
            mapped_df.loc[idx, 'Label'] = coarse_label

        if not merge_consecutive:
            return CoarseLabelUtils._handle_special_case_of_date_entities(mapped_df), entity_tracking


        merged_entities: List[Series] = list()
        merged_tracking: Dict[str, Dict[str, Any]] = dict()
        
        i = 0
        while i < len(mapped_df):
            current_entity: Series = mapped_df.iloc[i].copy()
            current_coarse_label: str = current_entity['Label']

            consecutive_entities: List[Series] = [current_entity]
            j = i + 1
            
            while j < len(mapped_df):
                next_entity: Series = mapped_df.iloc[j]
                
                if (
                    next_entity['Label'] == current_coarse_label and
                    CoarseLabelUtils.are_entities_consecutive_generic(consecutive_entities[-1], next_entity, input_text)
                ):
                    consecutive_entities.append(next_entity)
                    j += 1
                else:
                    break
            
            if len(consecutive_entities) > 1:

                merged_entity: Series = consecutive_entities[0].copy()
                merged_entity['End'] = consecutive_entities[-1]['End']
                merged_entity['Token'] = input_text[merged_entity['Start']: merged_entity['End']]

                merged_id: str = f"{''.join([entity['Token_ID'] for entity in consecutive_entities])}"
                merged_entity['Token_ID'] = merged_id
                
                merged_tracking[merged_id] = {
                    'coarse_label': current_coarse_label,
                    'merged_token': merged_entity['Token'],
                    'start': merged_entity['Start'],
                    'end': merged_entity['End'],
                    'constituent_entities': list()
                }

                for entity in consecutive_entities:
                    original_info = entity_tracking[entity['Token_ID']]
                    merged_tracking[merged_id]['constituent_entities'].append({
                        'original_label': original_info['original_label'],
                        'original_token': original_info['original_token'],
                        'start': original_info['start'],
                        'end': original_info['end']
                    })
                
                merged_entities.append(merged_entity)
            else:
                merged_entities.append(current_entity)
                entity_id = current_entity['Token_ID']
                merged_tracking[entity_id] = entity_tracking[entity_id].copy()
            
            i = j

        merged_df: DataFrame = DataFrame(merged_entities)
        return CoarseLabelUtils._handle_special_case_of_date_entities(merged_df), merged_tracking
    
    @staticmethod
    def _handle_special_case_of_date_entities(annotation_df: DataFrame) -> DataFrame:
        """
        Special handling for 'DATE' entities to trim trailing periods
        
        :param annotation_df: DataFrame with columns ['Token_ID', 'Label', 'Start', 'End', 'Token']
        :return: DataFrame with adjusted 'DATE' entities
        """
        for _, row in annotation_df.iterrows():
            if row['Label'] == 'DATE':
                date_pattern = r'^\d{1,2}\.\d{1,2}\.\d{2,4}\.$'
                if re.match(date_pattern, row['Token']):
                    trimmed_token = row['Token'][:-1]
                    annotation_df.loc[annotation_df['Token_ID'] == row['Token_ID'], 'Token'] = trimmed_token
                    annotation_df.loc[annotation_df['Token_ID'] == row['Token_ID'], 'End'] -= 1
        
        return annotation_df

    @staticmethod
    def print_tracking_info(tracking_dict: Dict[str, Dict[str, Any]]) -> None:
        """
        Print detailed tracking information
        
        :param tracking_dict: Dictionary containing tracking information for entities
        :return: None
        """
        print("\n" + "="*80)
        print("ENTITY TRACKING INFORMATION")
        print("="*80)
        
        for entity_id, info in tracking_dict.items():
            print(f"\nEntity ID: {entity_id}")
            print(f"Coarse Label: {info['coarse_label']}")
            
            if 'constituent_entities' in info:
                print(f"Merged Token: '{info['merged_token']}'")
                print(f"Position: {info['start']}-{info['end']}")
                print("Constituent entities:")
                for i, constituent in enumerate(info['constituent_entities'], 1):
                    print(f"  {i}. {constituent['original_label']}: '{constituent['original_token']}' ({constituent['start']}-{constituent['end']})")
            else:
                print(f"Original Label: {info['original_label']}")
                print(f"Original Token: '{info['original_token']}'")
                print(f"Position: {info['start']}-{info['end']}")
            print("-" * 40)