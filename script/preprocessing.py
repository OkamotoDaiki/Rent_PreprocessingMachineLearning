import numpy as np
import pandas as pd
import sys

def main():
    scraping_data_path = sys.argv[1]
    df = pd.read_csv(scraping_data_path, encoding='utf-16')

    #立地を「路線+駅」と「～分」に分割
    df = pd.concat([df, df['立地1'].str.split(' 歩', expand=True)], axis=1).drop(['立地1'], axis=1)
    df.rename(columns={0: '立地11', 1: '徒歩1'}, inplace=True)
    df = pd.concat([df, df['立地2'].str.split(' 歩', expand=True)], axis=1).drop(['立地2'], axis=1)
    df.rename(columns={0: '立地21', 1: '徒歩2'}, inplace=True)
    df = pd.concat([df, df['立地3'].str.split(' 歩', expand=True)], axis=1).drop(['立地3'], axis=1)
    df.rename(columns={0: '立地31', 1: '徒歩3'}, inplace=True)

    #立地をさらに「路線」、「駅」、「～分に分割」  
    df = pd.concat([df, df['立地11'].str.split('/', expand=True)], axis=1).drop(['立地11'], axis=1)
    df.rename(columns={0: '路線1', 1: '駅1'}, inplace=True)
    df = pd.concat([df, df['立地21'].str.split('/', expand=True)], axis=1).drop(['立地21'], axis=1)
    df.rename(columns={0: '路線2', 1: '駅2'}, inplace=True)
    df = pd.concat([df, df['立地31'].str.split('/', expand=True)], axis=1).drop(['立地31'], axis=1)
    df.rename(columns={0: '路線3', 1: '駅3'}, inplace=True)

    #「賃料」がNAの行を削除
    df.dropna(subset=['賃料'], inplace=True)  

    #数値として扱いたいので、不要な文字列を削除
    df['賃料'] = df['賃料'].str.replace('万円', '')
    df['管理費'] = df['管理費'].str.replace('円', '')
    df['築年数'] = df['築年数'].str.replace('新築', '0') #新築は築年数0年とする
    df['築年数'] = df['築年数'].str.replace('築', '')
    df['築年数'] = df['築年数'].str.replace('年', '')
    df['専有面積'] = df['専有面積'].str.replace('m2', '')
    df['敷金'] = df['敷金'].str.replace('万円', '')
    df['礼金'] = df['礼金'].str.replace('万円', '')
    df['徒歩1'] = df['徒歩1'].str.replace('分', '')
    df['徒歩2'] = df['徒歩2'].str.replace('分', '')
    df['徒歩3'] = df['徒歩3'].str.replace('分', '')

    #「-」を0に変換
    df['管理費'] = df['管理費'].replace('-',0)
    df['敷金'] = df['敷金'].replace('-',0)
    df['礼金'] = df['礼金'].replace('-',0)

    #文字列から数値に変換
    df['賃料'] = pd.to_numeric(df['賃料'])
    df['管理費'] = pd.to_numeric(df['管理費'])
    df['敷金'] = pd.to_numeric(df['敷金'])
    df['礼金'] = pd.to_numeric(df['礼金'])
    df['築年数'] = pd.to_numeric(df['築年数'])
    df['専有面積'] = pd.to_numeric(df['専有面積'])
    df['徒歩1'] = pd.to_numeric(df['徒歩1'])
    df['徒歩2'] = pd.to_numeric(df['徒歩2'])
    df['徒歩3'] = pd.to_numeric(df['徒歩3'])

    #単位を合わせるために、管理費以外を10000倍。
    df['賃料'] = df['賃料'] * 10000
    df['敷金'] = df['敷金'] * 10000
    df['礼金'] = df['礼金'] * 10000

    #毎月支払う家賃の指標
    df['賃料+管理費'] = df['賃料'] + df['管理費']
    #初期費用
    df['敷/礼'] = df['敷金'] + df['礼金']

    #住所を都道府県、～区、市町村番地に分割
    df = pd.concat([df, df['住所'].str.split('都', expand=True)], axis=1).drop(['住所'], axis=1)
    df.rename(columns={0: '都', 1: '市町村'}, inplace=True)
    df['都'] = df['都'] + '都'
    df = pd.concat([df, df['市町村'].str.split('区', expand=True)], axis=1).drop(['市町村'], axis=1)
    df.rename(columns={0: '区', 1: '区域'}, inplace=True)
    df['区'] = df['区'] + '区'

    #階を数値化
    df = pd.concat([df, df['階'].str.split('-', expand=True)], axis=1).drop(['階'], axis=1)
    df.rename(columns={0: '階', 1: '階2'}, inplace=True)
    df.drop(['階2'], axis=1, inplace=True)
    df['階'] = df['階'].str.replace('階', '')
    df['階'] = df['階'].str.replace('B', '-')
    df['階'] = df['階'].str.replace('M', '')
    df['階'] = pd.to_numeric(df['階'])

    #建物高さを数値化。地下は無視
    df['建物高さ'] = df['建物高さ'].str.replace('地下1地上', '')
    df['建物高さ'] = df['建物高さ'].str.replace('地下2地上', '')
    df['建物高さ'] = df['建物高さ'].str.replace('地下3地上', '')
    df['建物高さ'] = df['建物高さ'].str.replace('地下4地上', '')
    df['建物高さ'] = df['建物高さ'].str.replace('地下5地上', '')
    df['建物高さ'] = df['建物高さ'].str.replace('地下6地上', '')
    df['建物高さ'] = df['建物高さ'].str.replace('地下7地上', '')
    df['建物高さ'] = df['建物高さ'].str.replace('地下8地上', '')
    df['建物高さ'] = df['建物高さ'].str.replace('地下9地上', '')
    df['建物高さ'] = df['建物高さ'].str.replace('平屋', '1')
    df['建物高さ'] = df['建物高さ'].str.replace('階建', '')
    df['建物高さ'] = pd.to_numeric(df['建物高さ'])

    #間取りを「部屋数」、「DK有無」、「K有無」、「L有無」、「S有無」に分割
    df['間取りDK'] = 0
    df['間取りK'] = 0
    df['間取りL'] = 0
    df['間取りS'] = 0
    df['間取り'] = df['間取り'].str.replace('ワンルーム', '1')

    for i in range(len(df)):
        if 'DK' in df['間取り'][i]:
            df.loc[i, '間取りDK'] = 1
    df['間取り'] = df['間取り'].str.replace('DK', '')

    for j in range(len(df)):
        if 'DK' in df['間取り'][j]:
            df.loc[j, '間取りK'] = 1
    df['間取り'] = df['間取り'].str.replace('K', '')

    for k in range(len(df)):
        if 'L' in df['間取り'][k]:
            df.loc[k, '間取りL'] = 1
    df['間取り'] = df['間取り'].str.replace('L', '')

    for l in range(len(df)):
        if 'S' in df['間取り'][l]:
            df.loc[l, '間取りS'] = 1
    df['間取り'] = df['間取り'].str.replace('S', '')

    df['間取り'] = pd.to_numeric(df['間取り'])

    #カラムの入れ替え
    df = df.reindex(columns=['マンション名','都','区','区域','間取り','間取りDK','間取りK','間取りL','間取りS','築年数','建物高さ','階','専有面積','賃料+管理費','敷/礼',
                '路線1','駅1','徒歩1','路線2','駅2','徒歩2','路線3','駅3','徒歩3','賃料','管理費',
                '敷金','礼金'])

    #NaNになり得る列の削除
    df.drop(['路線2', '駅2', '徒歩2', '路線3', '駅3', '徒歩3'], axis=1, inplace=True)
    #NaNが含まれる行を削除
    df.dropna(inplace=True)

    #int64にキャスト
    df['階'] = df['階'].astype(np.int64)
    df['専有面積'] = df['専有面積'].astype(np.int64)
    df['賃料+管理費'] = df['賃料+管理費'].astype(np.int64)
    df['敷/礼'] = df['敷/礼'].astype(np.int64)
    df['徒歩1'] = df['徒歩1'].astype(np.int64)
    df['賃料'] = df['賃料'].astype(np.int64)
    df['管理費'] = df['管理費'].astype(np.int64)
    df['敷金'] = df['敷金'].astype(np.int64)
    df['礼金'] = df['礼金'].astype(np.int64)

    #csvに出力
    outputfpath = sys.argv[2]
    df.to_csv(outputfpath, index=False)

    return 0

if __name__=="__main__":
    main()