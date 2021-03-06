# -*- coding: utf-8 -*-

import numpy as np


class SparseSparseDataFrameSummary(dict):
    
    def __init__(self, summary_data, summary_idx, sdf=None):
        self["summary_data"] = summary_data
        self["summary_idx"] = summary_idx
        
        if sdf != None:
            self["sdf"] = sdf
            
        
    def __lt__(self, upper_bound):
        return type(self)(summary_data = self["summary_data"] < upper_bound,
                          summary_idx = self["summary_idx"],
                          sdf = self["sdf"])
    
    def __le__(self, upper_bound):
        return type(self)(summary_data = self["summary_data"] <= upper_bound,
                          summary_idx = self["summary_idx"],
                          sdf = self["sdf"])
    
    def __gt__(self, lower_bound):
        return type(self)(summary_data = self["summary_data"] > lower_bound,
                          summary_idx = self["summary_idx"],
                          sdf = self["sdf"])
        
    def __ge__(self, lower_bound):
        return type(self)(summary_data = self["summary_data"] > lower_bound,
                              summary_idx = self["summary_idx"],
                              sdf = self["sdf"])
    
    
    def __and__(self, other_summary):
        assert isinstance(other_summary, type(self))
        assert np.array_equal(self["summary_idx"],other_summary["summary_idx"])
        assert self['summary_data'].dtype == np.bool
        assert other_summary['summary_data'].dtype == np.bool
        
        return type(self)(summary_data = self["summary_data"] &  other_summary['summary_data'],
                          summary_idx = self["summary_idx"],
                          sdf = self["sdf"])
        
    @property
    def _is_bool(self):
        return self['summary_data'].dtype == np.bool
    
    @property
    def _has_sdf(self):
        return "sdf" in self.keys()
    
    @property
    def _filtered_summary_idx(self):
        assert self._is_bool
        
        return self["summary_idx"][self['summary_data']]
        
    @property
    def _sub_sdf(self):
        assert self._is_bool and self._has_sdf
        
        if self["sdf"].is_matched_col_shape(self['summary_data']):        
            return self["sdf"].sub_sdf(select_col = self['summary_data'])
        
        if self["sdf"].is_matched_row_shape(self['summary_data']):        
            return self["sdf"].sub_sdf(select_row = self['summary_data'])
        


class SparseDataFrame(dict):
    kmapper = {"sdtm":"smatrix"}
    
    def __init__(self, smatrix, col_idx=None, row_idx=None):
        self["smatrix"] = smatrix
        
        if col_idx != None:
            assert isinstance(col_idx, (list, np.ndarray))
            
            if isinstance(col_idx, list):
                assert self["smatrix"].shape[1] == len(col_idx)
                self["col_idx"] = np.array(col_idx)
                
            else:
                assert self["smatrix"].shape[1] == col_idx.shape[0]
                self["col_idx"] = np.array(col_idx)
        else:
            self["col_idx"] = np.arange(self["smatrix"].shape[1])
            
            
                
        if row_idx != None:
            assert isinstance(row_idx, (list, np.ndarray))
            
            if isinstance(row_idx, list):
                assert self["smatrix"].shape[0] == len(row_idx)
                self["row_idx"] = np.array(row_idx)
                
            else:
                assert self["smatrix"].shape[0] == row_idx.shape[0]
                self["row_idx"] = np.array(row_idx)
                
        else:
            self["row_idx"] = np.arange(self["smatrix"].shape[0])
    
    
    
    def __getattr__(self, key):
        
        if key.startswith("_") and key[1:] in self.keys():
            return self[key[1:]]
        else:
            
            if key.startswith("_") and key[1:] in self.kmapper.keys() and self.kmapper[key[1:]] in self.keys():
                return self[self.kmapper[key[1:]]]
            else:
                return None
        
#     @property
#     def _smatrix(self):
#         return self["smatrix"]
    
#     @property
#     def _col_idx(self):
#         return self["col_idx"]
    
#     @property
#     def _row_idx(self):
#         return self["row_idx"]

    @property
    def T(self):
        tr_sdf = type(self)(smatrix = self["smatrix"].T,
                            col_idx = self["row_idx"],
                            row_idx = self["col_idx"])
        return tr_sdf
    
    
    def summarize_sdf(self, summarizer=lambda xx:xx.sum(axis=0)):
    
        summary_data = summarizer(self["smatrix"])
        
        if len(summary_data.shape) == 1:
            _summary_data = summary_data
        else:
            assert len(summary_data.shape) == 2
            assert summary_data.shape[0] == 1 or summary_data.shape[1] == 1
            
            if summary_data.shape[0] == 1:
                _summary_data = np.array(summary_data)[0,:]
            else:
                _summary_data = np.array(summary_data)[:,0]
            
        
        if _summary_data.shape[0] == self["smatrix"].shape[0]:
            return SparseSparseDataFrameSummary(summary_data = _summary_data,
                                                summary_idx = self["row_idx"],
                                                sdf = self)
            
        if _summary_data.shape[0] == self["smatrix"].shape[1]:
            return SparseSparseDataFrameSummary(summary_data = _summary_data,
                                                summary_idx = self["col_idx"],
                                                sdf = self)

        
    def sub_sdf(self, select_col = None, select_row = None):
        
        if select_col != None:
            _select_col_idx = select_col
        else:
            _select_col_idx = np.arange(len(self["col_idx"]))

        new_col_idx = self["col_idx"][_select_col_idx]
        
        if select_row != None:
            _select_row_idx = select_row
        else:
            _select_row_idx = np.arange(len(self["row_idx"]))

        new_row_idx = self["row_idx"][_select_row_idx]
        
        new_smatrix = self["smatrix"][_select_row_idx,:][:,_select_col_idx]
        
        return type(self)(smatrix = new_smatrix,
                          col_idx = new_col_idx,
                          row_idx = new_row_idx)
    
    
    def is_matched_col_shape(self, vec):
        if isinstance(vec, list):
            return len(vec) == self["smatrix"].shape[1]
        
        if isinstance(vec, np.ndarray):
            assert len(vec.shape) == 1
            return vec.shape[0] == self["smatrix"].shape[1]
        
    def is_matched_row_shape(self,vec):
        if isinstance(vec, list):
            return len(vec) == self["smatrix"].shape[0]
        
        if isinstance(vec, np.ndarray):
            assert len(vec.shape) == 1
            return vec.shape[0] == self["smatrix"].shape[0]
            
        
    def is_col_vec(self,vec):
        return self.is_matched_row_shape(vec)
        
        
    def is_row_vec(self,vec):
        return self.is_matched_col_shape(vec)
        

if __name__ == '__main__':
    pass