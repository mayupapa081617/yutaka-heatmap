import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title='豊さんの株式ヒートマップ',layout='wide')
st.title('日本株・売買代金ヒートマップ【Ver.5】')
st.caption('無料データを利用。売買代金とその前日比は日足の終値×出来高による概算です。リアルタイムではありません。')

DEFAULT = '''半導体,8035,東京エレクトロン
半導体,6857,アドバンテスト
半導体,6920,レーザーテック
半導体,7735,SCREEN
半導体,6323,ローツェ
半導体,6146,ディスコ
半導体,6723,ルネサス
半導体,6526,ソシオネクスト
半導体,6315,TOWA
半導体,6963,ローム
電線・電子部品,5803,フジクラ
電線・電子部品,5801,古河電工
電線・電子部品,5802,住友電工
電線・電子部品,6981,村田製作所
電線・電子部品,6762,TDK
電線・電子部品,6976,太陽誘電
電線・電子部品,6504,富士電機
電線・電子部品,6645,オムロン
電線・電子部品,4062,イビデン
電線・電子部品,6807,日本航空電子
AI・データセンター,3905,データセクション
AI・データセンター,3778,さくらインターネット
AI・データセンター,9984,ソフトバンクG
AI・データセンター,6702,富士通
AI・データセンター,6701,NEC
AI・データセンター,9432,NTT
AI・データセンター,9433,KDDI
AI・データセンター,6501,日立製作所
AI・データセンター,3774,IIJ
AI・データセンター,4684,オービック
防衛・宇宙,7011,三菱重工
防衛・宇宙,7012,川崎重工
防衛・宇宙,7013,IHI
防衛・宇宙,6208,石川製作所
防衛・宇宙,4274,細谷火工
防衛・宇宙,7721,東京計器
防衛・宇宙,6946,日本アビオニクス
防衛・宇宙,7224,新明和工業
防衛・宇宙,6701,NEC
防衛・宇宙,9348,ispace
サイバーセキュリティ,4704,トレンドマイクロ
サイバーセキュリティ,3692,FFRIセキュリティ
サイバーセキュリティ,4441,トビラシステムズ
サイバーセキュリティ,3040,ソリトンシステムズ
サイバーセキュリティ,3962,チェンジHD
サイバーセキュリティ,4398,ブロードバンドセキュリティ
サイバーセキュリティ,4493,サイバーセキュリティクラウド
サイバーセキュリティ,4417,グローバルセキュリティエキスパート
サイバーセキュリティ,4288,アズジェント
サイバーセキュリティ,2326,デジタルアーツ
自動運転・ロボット,5255,ダイナミックマップ
自動運転・ロボット,6902,デンソー
自動運転・ロボット,7203,トヨタ自動車
自動運転・ロボット,6954,ファナック
自動運転・ロボット,6506,安川電機
自動運転・ロボット,6861,キーエンス
自動運転・ロボット,6324,ハーモニック・ドライブ
自動運転・ロボット,6222,島精機製作所
自動運転・ロボット,6273,SMC
自動運転・ロボット,6232,ACSL
電力・蓄電池・エネルギー,9501,東京電力HD
電力・蓄電池・エネルギー,9502,中部電力
電力・蓄電池・エネルギー,9503,関西電力
電力・蓄電池・エネルギー,9506,東北電力
電力・蓄電池・エネルギー,9513,Jパワー
電力・蓄電池・エネルギー,9508,九州電力
電力・蓄電池・エネルギー,6674,GSユアサ
電力・蓄電池・エネルギー,5019,出光興産
電力・蓄電池・エネルギー,5020,ENEOS
電力・蓄電池・エネルギー,9519,レノバ
銀行・金融,8306,三菱UFJ
銀行・金融,8316,三井住友FG
銀行・金融,8411,みずほFG
銀行・金融,8308,りそなHD
銀行・金融,7182,ゆうちょ銀行
銀行・金融,8591,オリックス
銀行・金融,8604,野村HD
銀行・金融,8601,大和証券G
銀行・金融,8473,SBI HD
銀行・金融,8697,日本取引所G
建設・インフラ・素材,1801,大成建設
建設・インフラ・素材,1802,大林組
建設・インフラ・素材,1803,清水建設
建設・インフラ・素材,1812,鹿島建設
建設・インフラ・素材,1925,大和ハウス
建設・インフラ・素材,1928,積水ハウス
建設・インフラ・素材,5401,日本製鉄
建設・インフラ・素材,5411,JFE HD
建設・インフラ・素材,5713,住友金属鉱山
建設・インフラ・素材,5233,太平洋セメント
人気テーマ・短期資金監視,7014,名村造船所
人気テーマ・短期資金監視,7003,三井E&S
人気テーマ・短期資金監視,6525,KOKUSAI ELECTRIC
人気テーマ・短期資金監視,5255,ダイナミックマップ
人気テーマ・短期資金監視,3350,メタプラネット
人気テーマ・短期資金監視,4588,オンコリス
人気テーマ・短期資金監視,4592,サンバイオ
人気テーマ・短期資金監視,4565,ネクセラファーマ
人気テーマ・短期資金監視,5253,カバー
人気テーマ・短期資金監視,4385,メルカリ'''

with st.sidebar:
    st.header('銘柄リスト')
    raw = st.text_area('1行ずつ「セクター,証券コード,銘柄名」', DEFAULT, height=400)
    st.caption('暫定100銘柄です。前回リストと異なる場合はここで編集できます。編集後「データ更新」を押してください。')
    run = st.button('🔄 データ更新',type='primary',use_container_width=True)

@st.cache_data(ttl=900,show_spinner=False)
def fetch(raw):
    items=[]
    for line in raw.splitlines():
        parts=[x.strip() for x in line.split(',')]
        if len(parts)!=3 or not(parts[1].isdigit() and len(parts[1])==4):
            continue
        items.append((parts[0],parts[1],parts[2]))
    if not items:
        return pd.DataFrame(), ['銘柄リストが空です。']
    tickers=list(dict.fromkeys(f'{code}.T' for _,code,_ in items))
    try:
        data=yf.download(tickers,period='8d',interval='1d',auto_adjust=False,progress=False,threads=True,group_by='ticker')
    except Exception as e:
        return pd.DataFrame(),[str(e)]
    records=[]; errors=[]
    for sector,code,name in items:
        ticker=f'{code}.T'
        try:
            frame=data[ticker] if isinstance(data.columns,pd.MultiIndex) else data
            frame=frame.dropna(subset=['Close','Volume'])
            if len(frame)<2: raise ValueError('比較に必要な2営業日分のデータなし')
            last=frame.iloc[-1]; prev=frame.iloc[-2]
            close=float(last['Close']); prev_close=float(prev['Close']); vol=float(last['Volume'])
            prev_vol=float(prev['Volume'])
            if prev_close<=0 or close<=0 or vol<=0 or prev_vol<=0: raise ValueError('有効な価格・出来高なし')
            today_value=close*vol/1e8
            prev_value=prev_close*prev_vol/1e8
            value_change=(today_value/prev_value-1)*100
            records.append({'セクター':sector,'コード':code,'銘柄':name,'騰落率(%)':(close/prev_close-1)*100,'概算売買代金(億円)':today_value,'前営業日概算売買代金(億円)':prev_value,'売買代金前日比(%)':value_change,'終値':close,'出来高':int(vol),'日付':str(frame.index[-1].date())})
        except Exception as e:
            errors.append(f'{code} {name}: {e}')
    return pd.DataFrame(records),errors

if run:
    fetch.clear()
with st.spinner('株価データを取得しています…'):
    df,errors=fetch(raw)
if df.empty:
    st.error('データを取得できませんでした。ネット接続や銘柄コードを確認して、再度更新してください。')
else:
    latest=', '.join(sorted(df['日付'].unique()))
    st.caption(f'取得した取引日: {latest} ／ 表示銘柄: {len(df)} ／ 更新操作時刻: {datetime.now():%Y-%m-%d %H:%M}')
    st.info('マスの面積＝概算売買代金、赤＝株価上昇、緑＝株価下落。金額と前日比は終値×出来高の概算です。複数セクターにある銘柄は重複集計されます。')
    # ランキングは同一コードの重複を除外（セクター別の集計は従来仕様）。
    unique_df=df.drop_duplicates(subset=['コード']).copy()
    # 3つのランキングを横並びでコンパクトに表示。
    min_value=st.sidebar.number_input('ランキング対象の最低概算売買代金（億円）',min_value=0.0,value=1.0,step=1.0)
    sector_rank=df.groupby('セクター',as_index=False)[['概算売買代金(億円)','前営業日概算売買代金(億円)']].sum()
    sector_rank['代金増減%']=(sector_rank['概算売買代金(億円)']/sector_rank['前営業日概算売買代金(億円)']-1)*100
    sector_rank=sector_rank.nlargest(10,'概算売買代金(億円)')
    eligible=unique_df[unique_df['概算売買代金(億円)']>=min_value]
    top_volume=eligible.nlargest(10,'売買代金前日比(%)')
    both=eligible[(eligible['騰落率(%)']>0)&(eligible['売買代金前日比(%)']>0)].copy()
    if not both.empty:
        both['株価順位']=both['騰落率(%)'].rank(ascending=False,method='min')
        both['代金順位']=both['売買代金前日比(%)'].rank(ascending=False,method='min')
        both['総合順位スコア']=both['株価順位']+both['代金順位']
        both=both.sort_values(['総合順位スコア','概算売買代金(億円)'],ascending=[True,False]).head(10)
    left,mid,right=st.columns(3,gap='small')
    with left:
        st.markdown('**📊 セクター売買代金 TOP10**')
        show=sector_rank[['セクター','概算売買代金(億円)','代金増減%']].copy()
        show.columns=['セクター','億円','前日比%']
        st.dataframe(show.style.format({'億円':'{:,.0f}','前日比%':'{:+.0f}%'}),hide_index=True,use_container_width=True,height=212)
    with mid:
        st.markdown('**🚀 売買代金増加 TOP10**')
        show=top_volume[['銘柄','概算売買代金(億円)','売買代金前日比(%)']].copy()
        show.columns=['銘柄','億円','前日比%']
        st.dataframe(show.style.format({'億円':'{:,.1f}','前日比%':'{:+.0f}%'}),hide_index=True,use_container_width=True,height=212)
    with right:
        st.markdown('**🔥 株価上昇＋代金増加 TOP10**')
        if both.empty:
            st.info('該当銘柄なし')
        else:
            show=both[['銘柄','騰落率(%)','売買代金前日比(%)']].copy()
            show.columns=['銘柄','株価%','代金%']
            st.dataframe(show.style.format({'株価%':'{:+.1f}%','代金%':'{:+.0f}%'}),hide_index=True,use_container_width=True,height=212)
    st.caption('ランキングは登録銘柄のみ。銘柄ランキングは重複除外、セクター合計は複数所属銘柄を各セクターに計上。売買代金は概算でリアルタイムではありません。')
    st.subheader('🟥 セクター別ヒートマップ')
    df['表示']=(df['銘柄']+'<br>'+df['騰落率(%)'].map(lambda x:f'{x:+.2f}%')+'<br>'+df['概算売買代金(億円)'].map(lambda x:f'{x:,.1f}億円')+'<br>'+df['売買代金前日比(%)'].map(lambda x:f'代金前日比 {x:+.1f}%'))
    df['色']=df['騰落率(%)'].apply(lambda x:'上昇' if x>0 else ('下落' if x<0 else '変わらず'))
    # Discrete red/green scheme is standard in Japanese markets.
    fig=px.treemap(df,path=[px.Constant('全銘柄'),'セクター','表示'],values='概算売買代金(億円)',color='色',
        color_discrete_map={'上昇':'#c93838','下落':'#16835a','変わらず':'#777777'},
        custom_data=['コード','終値','概算売買代金(億円)','騰落率(%)','日付','前営業日概算売買代金(億円)','売買代金前日比(%)'])
    fig.update_traces(textinfo='label',hovertemplate='銘柄: %{label}<br>コード: %{customdata[0]}<br>終値: %{customdata[1]:,.1f}円<br>概算売買代金: %{customdata[2]:,.1f}億円<br>騰落率: %{customdata[3]:+.2f}%<br>前営業日概算代金: %{customdata[5]:,.1f}億円<br>売買代金前日比: %{customdata[6]:+.1f}%<br>日付: %{customdata[4]}<extra></extra>',root_color='#181818')
    fig.update_layout(height=680,margin=dict(t=5,l=5,r=5,b=5),font=dict(size=15))
    st.plotly_chart(fig,use_container_width=True)
    st.caption('前日比＝（直近営業日の概算売買代金 ÷ 前営業日の概算売買代金 − 1）×100。休場日には直近の取引日を使用します。小さいマスでは文字が省略されるため、マウスを重ねて詳細を確認してください。')
    st.subheader('セクター別・概算売買代金ランキング')
    rank=df.groupby('セクター',as_index=False)[['概算売買代金(億円)','前営業日概算売買代金(億円)']].sum()
    rank['売買代金前日比(%)']=(rank['概算売買代金(億円)']/rank['前営業日概算売買代金(億円)']-1)*100
    rank=rank.sort_values('概算売買代金(億円)',ascending=False)
    st.dataframe(rank,use_container_width=True,hide_index=True)
    st.download_button('取得データをCSV保存',df.drop(columns=['表示','色']).to_csv(index=False).encode('utf-8-sig'),'heatmap_data.csv','text/csv')
if errors:
    with st.expander(f'取得できなかった銘柄・注意事項（{len(errors)}件）'):
        st.write('\n'.join(errors))
st.caption('投資判断の前に証券会社の正式な売買代金・株価を確認してください。')
