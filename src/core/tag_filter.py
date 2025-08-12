"""Tag filtering and management"""

import pandas as pd
from typing import Set, List, Optional
from ..logging_config import get_main_logger

class TagFilter:
    """Filter tests by tags with AND/OR logic"""
    
    def __init__(self, include_tags: Optional[List[str]] = None, 
                 exclude_tags: Optional[List[str]] = None,
                 require_all: bool = False):
        self.include_tags = set(include_tags or [])
        self.exclude_tags = set(exclude_tags or [])
        self.require_all = require_all  # True = AND logic, False = OR logic
        self.logger = get_main_logger()
    
    def matches(self, test_tags: str) -> bool:
        """Check if test matches filter criteria"""
        if not test_tags:
            test_tag_set = set()
        else:
            test_tag_set = set(tag.strip() for tag in test_tags.split(',') if tag.strip())
        
        # Check exclude tags first
        if self.exclude_tags and (test_tag_set & self.exclude_tags):
            return False
        
        # Check include tags
        if self.include_tags:
            if self.require_all:
                # AND logic - test must have ALL include tags
                return self.include_tags.issubset(test_tag_set)
            else:
                # OR logic - test must have at least ONE include tag
                return bool(test_tag_set & self.include_tags)
        
        return True  # No include filter = match all (except excluded)
    
    def filter_tests(self, tests_df: pd.DataFrame) -> pd.DataFrame:
        """Filter tests DataFrame by tags"""
        if not self.include_tags and not self.exclude_tags:
            return tests_df
        
        mask = tests_df['tags'].fillna('').apply(self.matches)
        filtered = tests_df[mask]
        
        self.logger.info(f"🏷️ Tag filter applied: {len(tests_df)} → {len(filtered)} tests")
        if self.include_tags:
            self.logger.debug(f"Include tags: {self.include_tags} ({'AND' if self.require_all else 'OR'} logic)")
        if self.exclude_tags:
            self.logger.debug(f"Exclude tags: {self.exclude_tags}")
        
        return filtered
    
    @staticmethod
    def get_all_tags(tests_df: pd.DataFrame) -> Set[str]:
        """Extract all unique tags from tests"""
        all_tags = set()
        for tags_str in tests_df['tags'].fillna(''):
            if tags_str:
                tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                all_tags.update(tags)
        return all_tags