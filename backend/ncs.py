import pandas as pd
import numpy as np

class NCSData(object):
    files = {
        1: 'data/ncs/230105/01_classification.csv',
        2: 'data/ncs/230105/02_ncsJobInfo.csv',
        3: 'data/ncs/230105/03_competencyUnit.csv',
        # 4: 'ncs/230105/04_competencyUnitElement.csv',
        5: 'data/ncs/230105/05_performCrit.csv',
        # 6: 'ncs/230105/06_compUnitAppBound.csv',
        # 71: 'ncs/230105/07_1_compUnitCsdrData.csv',
        # 72: 'ncs/230105/07_2_compUnitEvalData.csv',
        8: 'data/ncs/230105/08_compUnitJob.csv',
        # 9: 'ncs/230105/09_jobPosition.csv',
        # 10: 'ncs/230105/10_relatedCompUnit.csv',
        # 11: 'ncs/230105/11_trainKeyConsider.csv',
        # 13: 'ncs/230105/13_compQuestionKey.csv'
    }

    def __init__(self):
        NCS1 = pd.read_csv(self.files[1], index_col=0).set_index(['ncsLclasCd', 'ncsMclasCd', 'ncsSclasCd', 'ncsSubdCd']).drop('ncsDegr', axis=1)
        NCS1['dutyCd'] = NCS1.index.map(lambda idx: self.idx2cd(idx))
        self._cls_df = NCS1

        self._duty_df = pd.read_csv(self.files[2], dtype={'dutyCd': str}, index_col=0).set_index('dutyCd')

        NCS3 = pd.read_csv(self.files[3], dtype={'dutyCd': str, 'compUnitCd':str, 'compUnitLevel':int, 'compUnitName': str}, index_col=0).set_index(['dutyCd', 'compUnitCd'])
        NCS3['compUnitName'] = NCS3.compUnitName.apply(lambda x: x[3:])
        self._comp_unit_df = NCS3

        NCS5 = pd.read_csv(self.files[5], dtype={'dutyCd': str, 'compUnitCd': str, 'compUnitFactrName': str}, index_col=0).set_index(['dutyCd', 'compUnitCd', 'compUnitFactrNo', 'gbnCd'])
        # NCS5 has 12 missing values (2023.01.05.)
        # Try `NCS5[NCS5.isna().any(axis=1)]` and fill the values.
        NCS5 = NCS5.dropna()
        NCS5['compUnitFactrName'] = NCS5.compUnitFactrName.apply(lambda x: x[2:])
        NCS5['gbnVal'] = NCS5.gbnVal.apply(lambda x: x[2:])
        self._gbn_df = NCS5

        NCS8 = pd.read_csv(self.files[8], dtype={'code': str, 'mainNo': int, 'subNo': int})
        # NCS8 has missing the descriptions for dutyCd 24010402 농림어업_농업_화훼장식_공간화훼장식.
        # It yields the loss of one of score in the final search task.
        columns = ['dutyCd', 'compUnitCd'] + NCS8.columns[1:].tolist()
        NCS8['dutyCd'] = NCS8.code.apply(lambda x: x[:8])
        NCS8['compUnitCd'] = NCS8.code.apply(lambda x: x[-2:])
        NCS8 = NCS8[columns]
        self._key_comp_s = NCS8[['dutyCd', 'compUnitCd', 'mainNo']].drop_duplicates().set_index(['dutyCd', 'compUnitCd']).sort_index()

        self._key_comp_main_df = NCS8[['mainNo','mainName','mainDesc']].drop_duplicates().set_index('mainNo').sort_index()
        self._key_comp_sub_df = NCS8[['mainNo', 'mainName', 'subNo', 'subName', 'subDesc']].drop_duplicates().set_index(['mainNo','subNo']).sort_index()
    
    @staticmethod
    def idx2cd(idx):
        assert type(idx) == tuple
        return ''.join([f'{c:02d}' for c in idx])

    @staticmethod
    def cd2idx(cd):
        assert type(cd) == str
        assert len(cd)%2 == 0
        return tuple(int(''.join(t)) for t in zip(cd[::2], cd[1::2]))
        
    def getClsNms(self, dutyIdx):
        if type(dutyIdx) == str:
            dutyIdx = self.cd2idx(dutyIdx)
        return self._cls_df.loc[dutyIdx].iloc[0,:len(dutyIdx)].to_list()


class NCSText(NCSData):
    def __init__(self):
        super().__init__()
        self.duty_txt = self._duty_df['dutyDef']
        self.comp_unit_txt = self._comp_unit_df['compUnitDef']
        self.gbn_txt = self._gbn_df['gbnVal']
        self.key_comp_main_txt = self._key_comp_main_df['mainDesc']
        self.key_comp_sub_txt = self._key_comp_sub_df['subDesc']


class NCSFeature(NCSText):
    def __init__(self):
        super().__init__()
    
    def encode(self, encoder, *args, **kwargs):
        self.features = {}
        self.features['duty'] = encoder(self.duty_txt.to_list(), *args, **kwargs)
        self.features['comp_unit'] = encoder(self.comp_unit_txt.to_list(), *args, **kwargs)
        self.features['gbn'] = encoder(self.gbn_txt.to_list(), *args, **kwargs)
        self.features['key_comp_main'] = encoder(self.key_comp_main_txt.to_list(), *args, **kwargs)
        self.features['key_comp_sub'] = encoder(self.key_comp_sub_txt.to_list(), *args, **kwargs)

    def save_encoded_txt(self, file_name):
        assert hasattr(self, 'features'), "Encode first."
        np.savez(file_name, **self.features)

    def load_encoded_txt(self, file_name):
        assert not hasattr(self, 'features'), "Exist features already."
        self.features = np.load(file_name)

    def hfa(self):
        assert hasattr(self, 'features'), "Encode or load first."
        self.gbn_features_df = pd.DataFrame(self.features['gbn'], self.gbn_txt.index).groupby(level=[0,1,2,3]).mean()
        self.comp_unit_elt_features_df = self.gbn_features_df.groupby(level=[0,1,2]).mean()

        key_comp_main_features_df = pd.DataFrame(self.features['key_comp_main'], self.key_comp_main_txt.index)
        key_comp_main_features_df += pd.DataFrame(self.features['key_comp_sub'], self.key_comp_sub_txt.index).groupby(level=[0]).mean()
        key_comp_main_features_df /= 2
        key_comp_features_df = pd.DataFrame(self._key_comp_s).join(key_comp_main_features_df, on='mainNo').drop('mainNo')
        self.key_comp_features_df = key_comp_features_df.groupby(level=[0,1]).mean()

        comp_unit_features_df = pd.DataFrame(self.features['comp_unit'], self.comp_unit_txt.index)
        comp_unit_features_df += self.comp_unit_elt_features_df.groupby(level=[0,1]).mean()
        comp_unit_features_df += 2 * self.key_comp_features_df
        self.comp_unit_features_df = comp_unit_features_df / 4

        duty_features_df = pd.DataFrame(self.features['duty'], self.duty_txt.index)
        duty_features_df += comp_unit_features_df.groupby(level=[0]).mean()
        self.duty_features_df = duty_features_df / 5

        return self.duty_features_df, self.comp_unit_features_df
    
    def hfa2_duty(self):
        assert hasattr(self, 'features'), "Encode or load first."

        duty_features_df = pd.DataFrame(self.features['duty'], self.duty_txt.index)
        comp_unit_features_df = pd.DataFrame(self.features['comp_unit'], self.comp_unit_txt.index).groupby(level=[0]).mean()
        gbn_features_df = pd.DataFrame(self.features['gbn'], self.gbn_txt.index).groupby(level=[0]).mean()

        key_comp_main_features_df = pd.DataFrame(self.features['key_comp_main'], self.key_comp_main_txt.index)
        key_comp_main_features_df += pd.DataFrame(self.features['key_comp_sub'], self.key_comp_sub_txt.index).groupby(level=[0]).mean()
        key_comp_main_features_df /= 2
        key_comp_features_df = pd.DataFrame(self._key_comp_s).join(key_comp_main_features_df, on='mainNo').drop('mainNo', axis=1)
        key_comp_features_df = key_comp_features_df.groupby(level=[0]).mean()

        return duty_features_df, comp_unit_features_df, gbn_features_df, key_comp_features_df

    def hfa2_unit(self):
        assert hasattr(self, 'features'), "Encode or load first."

        comp_unit_features_df = pd.DataFrame(self.features['comp_unit'], self.comp_unit_txt.index).groupby(level=[0,1]).mean()
        gbn_features_df = pd.DataFrame(self.features['gbn'], self.gbn_txt.index).groupby(level=[0,1]).mean()

        key_comp_main_features_df = pd.DataFrame(self.features['key_comp_main'], self.key_comp_main_txt.index)
        key_comp_main_features_df += pd.DataFrame(self.features['key_comp_sub'], self.key_comp_sub_txt.index).groupby(level=[0]).mean()
        key_comp_main_features_df /= 2
        key_comp_features_df = pd.DataFrame(self._key_comp_s).join(key_comp_main_features_df, on='mainNo').drop('mainNo', axis=1)
        key_comp_features_df = key_comp_features_df.groupby(level=[0,1]).mean()

        return comp_unit_features_df, gbn_features_df, key_comp_features_df

    

if __name__ == '__main__':
    import os
    import argparse
    import pickle
    from engine.encoder import Encoder
    from engine.engine import Search

    parser = argparse.ArgumentParser(description='Generate NCS Search Engine')
    parser.add_argument('path', metavar='PATH', type=str, help='directory for saving generated search engine')
    parser.add_argument('--gpu', '-g', action='store_true', default=False, help='use gpu (default: False)')
    parser.add_argument('--encoder', '-e', metavar='ENCODER', type=str, default='BM-K/KoSimCSE-roberta-multitask', help='huggingface model name (defualt: BM-K/KoSimCSE-roberta-multitask)')
    parser.add_argument('--batch', '-b', metavar='BATCH_SIZE', type=int, default=128, help='batch size (default: 128)')
    parser.add_argument('--features', '-f', metavar='FNAME', type=str, default='features/ncs.npz', help='path of save file of encoded text (default: features/ncs.npz)')
    args = parser.parse_args()

    ncs = NCSFeature()
    if os.path.exists(args.features):
        ncs.load_encoded_txt(args.features)
    else:
        encoder = Encoder(args.encoder, 'cuda' if args.gpu else 'cpu')
        ncs.encode(encoder, batch_size=args.batch, prog_bar=True)
        ncs.save_encoded_txt(args.features)
        del ncs
        del encoder
        ncs = NCSFeature()
        ncs.load_encoded_txt(args.features)
    duty_df, comp_unit_df = ncs.hfa()

    duty_search = Search(duty_df, ncs._duty_df.dutyNm)
    comp_unit_search = Search(comp_unit_df, ncs._comp_unit_df.compUnitName)

    with open(os.path.join(args.path, 'duty_search.pickle'), 'wb') as f:
        pickle.dump(duty_search, f)
    with open(os.path.join(args.path, 'comp_unit_search.pickle'), 'wb') as f:
        pickle.dump(comp_unit_search, f)
