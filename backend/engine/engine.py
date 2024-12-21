import pandas as pd
import numpy as np

def softmax(x, temp=1.0, axis=0):
    x = x/temp
    return(np.exp(x - np.max(x)) / np.exp(x - np.max(x)).sum(axis=axis, keepdims=True))


class Search(object):
    def __init__(self, keys_df, values):
        mask = keys_df.notna().all(axis=1)
        keys_df = keys_df[mask]
        self.values = values[mask]
        self.idx = keys_df.index
        self.keys = keys_df.to_numpy()
        self.keys = self.keys / np.linalg.norm(self.keys, axis=1, keepdims=True)
    
    def score(self, query, top_k=10):
        q = query.mean(axis=0, keepdims=True)
        q = q / np.linalg.norm(q, axis=1, keepdims=True)
        
        score_df = pd.DataFrame((self.keys @ q.T), self.idx, ['Score'])
        score_df['Nm'] = self.values

        if top_k is None:
            return score_df
        return score_df.sort_values('Score', ascending=False).head(top_k)


class Search2(object):
    def __init__(self, keys_dfs:list, values:pd.Series):
        mask = pd.concat([df for df in keys_dfs], axis=1).notna().all(axis=1)
        self.idx = mask[mask].index
        self.values = values[self.idx]

        self.keys = np.stack([df.loc[self.idx].to_numpy() for df in keys_dfs])
        self.lv_attn_v = self.keys.mean(axis=-2)
        self.attn_v = self.lv_attn_v.mean(axis=0)

        self.keys = self.keys / np.linalg.norm(self.keys, axis=-1, keepdims=True)
        self.lv_attn_v = self.lv_attn_v / np.linalg.norm(self.lv_attn_v, axis=-1, keepdims=True)
        self.attn_v = self.attn_v / np.linalg.norm(self.attn_v, axis=-1, keepdims=True)
    
    def score(self, query, top_k=10, alpha=1.2, beta=0.042, attn_score=False):
        q = query / np.linalg.norm(query, axis=-1, keepdims=True)
        attn = softmax(self.attn_v @ q.T, temp=alpha)
        lv_attn = softmax(self.lv_attn_v @ q.T, temp=beta, axis=0)
        score = np.einsum('j, ij, ikl, jl', attn, lv_attn, self.keys, q)
        score = (score - score.min()) / (score.max() - score.min())

        score_df = pd.DataFrame(score, self.idx, ['Score'])
        score_df['Nm'] = self.values

        if attn_score:
            return score_df.sort_values('Score', ascending=False).head(top_k), (attn, lv_attn)
        return score_df.sort_values('Score', ascending=False).head(top_k)

class Search3(object):
    def __init__(self, keys_dfs:list, values:pd.Series):
        mask = pd.concat([df for df in keys_dfs], axis=1).notna().all(axis=1)
        self.idx = mask[mask].index
        self.values = values[self.idx]

        self.keys = np.stack([df.loc[self.idx].to_numpy() for df in keys_dfs]).mean(axis=0)
        self.attn_v = self.keys.mean(axis=0)

        self.keys = self.keys / np.linalg.norm(self.keys, axis=-1, keepdims=True)
        self.attn_v = self.attn_v / np.linalg.norm(self.attn_v, axis=-1, keepdims=True)
    
    def score(self, query, top_k=10, alpha=1.0, heat_map=False):
        q = query / np.linalg.norm(query, axis=-1, keepdims=True)
        attn = softmax(self.attn_v @ q.T, temp=alpha)
        score = (self.keys @ q.T) * attn

        score_df = pd.DataFrame(score.sum(axis=-1), self.idx, ['Score'])
        score_df = (score_df - score_df.min()) / (score_df.max() - score_df.min())
        score_df['Nm'] = self.values
        score_df = score_df.sort_values('Score', ascending=False).head(top_k)

        if heat_map:
            heat_map_df = pd.DataFrame((score - score.min())/(score.max() - score.min()), self.idx)
            return score_df, heat_map_df.T
        return score_df