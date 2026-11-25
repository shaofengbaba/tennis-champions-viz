from pathlib import Path
import pandas as pd
import numpy as np
D=Path(__file__).parent
p=pd.read_csv(D/'player_matches.csv'); e=pd.read_csv(D/'slam_entries.csv'); m=pd.read_csv(D/'player_year_matrix.csv')
# Canonicalize inconsistent spelling in every table used for filtering.
for f in ['player_matches','slam_entries','rivalry_matches','star_matches','star_slam_matches','all_slam_finals']:
 a=pd.read_csv(D/f'{f}.csv'); a['tourney_name']=a.tourney_name.replace({'Us Open':'US Open'}); a.to_csv(D/f'{f}.csv',index=False)
p.tourney_name=p.tourney_name.replace({'Us Open':'US Open'}); e.tourney_name=e.tourney_name.replace({'Us Open':'US Open'})
p['wins']=p.win*p.played; p['losses']=(1-p.win)*p.played
v=p.status.eq('completed') & p.svpt.gt(0) & p.ace.notna(); p['ace_n']=p.ace.where(v); p['ace_d']=p.svpt.where(v)
v=p.status.eq('completed') & p.svpt.gt(0)&p['1stWon'].notna()&p['2ndWon'].notna(); p['serve_n']=(p['1stWon']+p['2ndWon']).where(v); p['serve_d']=p.svpt.where(v)
def summarize(a,keys):
 g=a.groupby(keys,dropna=False).agg(recorded_matches=('match_id','size'),played_matches=('played','sum'),wins=('wins','sum'),losses=('losses','sum'),slam_titles=('slam_title','sum'),rank_sum=('player_rank','sum'),rank_n=('player_rank','count'),ace_matches=('ace_n','count'),aces=('ace_n','sum'),ace_service_points=('ace_d','sum'),serve_matches=('serve_n','count'),service_points_won=('serve_n','sum'),service_points=('serve_d','sum')).reset_index()
 for name,n,d in [('win_rate','wins','played_matches'),('rank_mean','rank_sum','rank_n'),('ace_rate','aces','ace_service_points'),('serve_win_rate','service_points_won','service_points')]: g[name]=g[n]/g[d].replace(0,np.nan)
 return g
base=['player_id','player_name','year']; frames=[]
for scope,a in [('all',p),('slam',p[p.slam])]:
 keys=base+['surface']; g=summarize(a,keys); g=g.merge(e.groupby(keys).size().rename('slam_entries').reset_index(),on=keys,how='left'); g.slam_entries=g.slam_entries.fillna(0).astype(int); g['scope']=scope; g['title_per_entry']=g.slam_titles/g.slam_entries.replace(0,np.nan); frames.append(g)
surf=pd.concat(frames,ignore_index=True); surf.to_csv(D/'player_year_surface.csv',index=False)
keys=base+['tourney_name','surface']; t=summarize(p[p.slam],keys).merge(e.groupby(keys).size().rename('slam_entries').reset_index(),on=keys,how='left'); t['title_per_entry']=t.slam_titles/t.slam_entries.replace(0,np.nan); t.to_csv(D/'player_year_tournament.csv',index=False)
# Distinguish participation from availability of a chosen metric.
m['cell_state']=np.select([~m.observed_season,m.slam_entries.fillna(0).eq(0),m.slam_titles.fillna(0).eq(0)],['no_record','no_slam_entry','zero_titles'],default='positive_titles')
for metric in ['slam_win_rate','win_rate','rank_mean','ace_rate','serve_win_rate']:
 m[metric+'_state']=np.where(~m.observed_season,'no_record',np.where((m.slam_entries.fillna(0).eq(0)) if metric=='slam_win_rate' else False,'no_slam_entry',np.where(m[metric].isna(),'missing_metric','available')))
m.to_csv(D/'player_year_matrix.csv',index=False)
# Year/surface/tournament filtering: join against full grid; preserve the distinction between no season and no selected entry.
assert len(m)==273 and m.slam_titles.sum()==94
assert t.slam_entries.sum()==373 and t.slam_titles.sum()==94
assert surf[surf.scope=='all'].played_matches.sum()==p.played.sum()
assert surf[surf.scope=='slam'].slam_titles.sum()==94
assert (t.wins+t.losses==t.played_matches).all()
print(m.cell_state.value_counts().to_string()); print('surface rows',len(surf),'tournament rows',len(t)); print('missing metrics',m.filter(like='_state').apply(lambda x:(x=='missing_metric').sum()).to_dict()); print('Nadal 2008',t[(t.player_name=='Rafael Nadal')&(t.year==2008)][['tourney_name','slam_titles','slam_entries','win_rate']].to_string(index=False))
