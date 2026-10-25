"""提取论文图表的真实数据（v6.0 RD binscatter + 密度 + SME 剂量反应）"""
import csv, io, os, sys, json, zipfile
import numpy as np

BASE = r'C:\Users\OMEN\Desktop\neo'
sys.path.insert(0, os.path.join(BASE, 'identification'))
TED = os.path.join(BASE, 'data', 'external', 'ted')

ISO2TO3 = {'AT':'AUT','BE':'BEL','BG':'BGR','HR':'HRV','CY':'CYP','CZ':'CZE','DK':'DNK',
           'EE':'EST','FI':'FIN','FR':'FRA','DE':'DEU','GR':'GRC','HU':'HUN','IE':'IRL',
           'IT':'ITA','LV':'LVA','LT':'LTU','LU':'LUX','MT':'MLT','NL':'NLD','PL':'POL',
           'PT':'PRT','RO':'ROU','SK':'SVK','SI':'SVN','ES':'ESP','SE':'SWE','UK':'GBR'}
THRESH = {
    2013:(207000,5235000),2014:(207000,5235000),2015:(207000,5235000),2016:(207000,5235000),
    2017:(207000,5235000),2018:(221000,5548000),2019:(221000,5548000),2020:(214000,5350000),
    2021:(214000,5350000),2022:(215000,5382000),2023:(215000,5382000),
}

def fnum(x):
    try: return float(x)
    except Exception: return None

def extract(band=0.20):
    rows=[]
    for fn in sorted(os.listdir(TED)):
        if not (fn.startswith('can_') and fn.endswith('.zip')): continue
        fy=int(fn[4:8])
        if fy not in THRESH: continue
        z=zipfile.ZipFile(os.path.join(TED,fn))
        with z.open(z.namelist()[0]) as f:
            for row in csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig')):
                code=ISO2TO3.get((row.get('ISO_COUNTRY_CODE') or '').strip())
                if not code: continue
                if (row.get('CANCELLED') or '0').strip()=='1': continue
                tc=(row.get('TYPE_OF_CONTRACT') or '').strip()
                if tc not in ('W','S','U'): continue
                v=fnum(row.get('AWARD_VALUE_EURO'))
                if v is None or v<=0: continue
                thr=THRESH[fy][1] if tc=='W' else THRESH[fy][0]
                if not (thr*(1-band)<=v<=thr*(1+band)): continue
                n=fnum(row.get('NUMBER_OFFERS')); ne=fnum(row.get('NUMBER_OFFERS_ELECTR'))
                rows.append({'r':np.log(v)-np.log(thr),'above':1 if v>=thr else 0,
                             'n':n,'single':1 if (n is not None and n==1) else 0,
                             'elec':(ne/n) if (n and n>=1 and ne is not None) else np.nan})
    return rows

print('提取 ±20% 样本...')
d=extract()
print(f'  {len(d):,} 份合同')
OUT=r'C:\Users\OMEN\Desktop\economy\figures'

# ---- 1. RD binscatter（单投标比例 by r 的 0.02 bin）----
bw=0.02
bins={}
for x in d:
    b=np.floor(x['r']/bw)
    bins.setdefault(b,{'n':0,'s':0,'e':0.0})
    bins[b]['n']+=1; bins[b]['s']+=x['single']
    if not np.isnan(x['elec']): bins[b]['e']+=x['elec']
bs=sorted(bins)
centers=[(b+0.5)*bw for b in bs]
share=[bins[b]['s']/bins[b]['n'] for b in bs]
counts=[bins[b]['n'] for b in bs]
elec=[bins[b]['e']/bins[b]['n'] for b in bs]
json.dump({'centers':centers,'share':share,'counts':counts,'elec':elec,'binwidth':bw},
          open(os.path.join(OUT,'rd_binscatter.json'),'w'))
print(f'  binscatter: {len(bs)} 个 bin（r ∈ [{centers[0]:.2f}, {centers[-1]:.2f}]）')

# ---- 2. 局部线性拟合线（±0.15 窗，两侧分别）----
r=np.array([x['r'] for x in d]); s=np.array([x['single'] for x in d])
ab=np.array([x['above'] for x in d])
lines={}
for side,mask in [('left',ab==0),('right',ab==1)]:
    rr=r[mask]; ss=s[mask]
    w=(np.abs(rr)<=0.15)
    c=np.polyfit(rr[w],ss[w],1)
    xs=np.linspace(-0.15,0,31) if side=='left' else np.linspace(0,0.15,31)
    lines[side]={'x':xs.tolist(),'y':np.polyval(c,xs).tolist()}
json.dump(lines, open(os.path.join(OUT,'rd_fitlines.json'),'w'))
print('  拟合线已计算（±0.15 窗，线性）')

# ---- 3. 密度直方图数据（已有 counts）----
json.dump({'centers':centers,'counts':counts}, open(os.path.join(OUT,'density.json'),'w'))
n_left=sum(bins[b]['n'] for b in bs if b<0); n_right=sum(bins[b]['n'] for b in bs if b>=0)
print(f'  密度: 左 {n_left:,} | 右 {n_right:,} | 差 {100*(n_right-n_left)/(n_left+n_right):+.1f}%')

# ---- 4. SME 剂量反应（从 ted_micro 面板）----
import pandas as pd
micro=pd.read_csv(os.path.join(BASE,'data','interim','ted_micro.csv'))
g=micro.groupby('elec_bin') if 'elec_bin' in micro.columns else None
# 用 run_v4 的口径：电子投标份额分箱
micro['eb']=pd.cut(micro['elec_share_contract'], bins=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0], include_lowest=True)
dose=micro.groupby('eb', observed=True).agg(sme=('sme_tender_share','mean'), n=('n_contracts','sum')).reset_index()
dose['mid']=[(i.left+i.right)/2 for i in dose['eb']]
dose[['mid','sme','n']].to_json(os.path.join(OUT,'sme_dose.json'), orient='records')
print(f'  剂量反应: {len(dose)} 个电子投标份额箱')

print('图表数据就绪 ->', OUT)
