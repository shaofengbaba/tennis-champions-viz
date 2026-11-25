import pandas as pd, numpy as np, zipfile, re, sys
from pathlib import Path
from itertools import combinations
src=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/tennis-atp-data-main.zip')
out=Path(__file__).parent
ids={101736:'Andre Agassi',101948:'Pete Sampras',103819:'Roger Federer',104745:'Rafael Nadal',104925:'Novak Djokovic',206173:'Jannik Sinner',207989:'Carlos Alcaraz'}
z=zipfile.ZipFile(src); files=sorted(n for n in z.namelist() if re.search(r'atp_matches_\d{4}\.csv$',n))
d=pd.concat([pd.read_csv(z.open(n),low_memory=False) for n in files],ignore_index=True)
d['date']=pd.to_datetime(d.tourney_date.astype(str),format='%Y%m%d',errors='coerce'); d['year']=d.date.dt.year; d['match_id']=d.tourney_id.astype(str)+'_'+d.match_num.astype(str)
d['status']=np.select([d.score.str.contains(r'W\s*/?\s*O|WALKOVER',case=False,na=False),d.score.str.contains('RET',case=False,na=False),d.score.str.contains('DEF',case=False,na=False),d.score.isna()],['walkover','retirement','default','unknown'],default='completed')
d['played']=d.status.isin(['completed','retirement','default']); d['slam']=d.tourney_level.eq('G'); d['title']=d.slam & d['round'].eq('F')
sub=d[d.winner_id.isin(ids)|d.loser_id.isin(ids)].copy(); sub.to_csv(out/'star_matches.csv',index=False)
sub[sub.slam].to_csv(out/'star_slam_matches.csv',index=False)
# one row per selected player per match, retaining opponents
parts=[]
for side,opp,p,q,win in [('winner','loser','w','l',1),('loser','winner','l','w',0)]:
 a=sub[sub[side+'_id'].isin(ids)].copy(); b=a[['match_id','tourney_id','tourney_name','date','year','surface','tourney_level','round','score','status','played','slam','minutes']].copy()
 for col in ['id','name','age','rank','rank_points','ht','hand','ioc','seed']: b['player_'+col]=a[side+'_'+col]; b['opponent_'+col]=a[opp+'_'+col]
 b['win']=win; b['slam_title']=a.title & bool(win)
 for col in ['ace','df','svpt','1stIn','1stWon','2ndWon','bpSaved','bpFaced']:
  b[col]=a[p+'_'+col]; b['opp_'+col]=a[q+'_'+col]
 parts.append(b)
p=pd.concat(parts,ignore_index=True).sort_values(['player_id','date','match_id']); p.to_csv(out/'player_matches.csv',index=False)
s=p[p.slam].copy(); rounds={'R128':1,'R64':2,'R32':3,'R16':4,'QF':5,'SF':6,'F':7}; s['stage']=s['round'].map(rounds)
s['played_win']=s.win*s.played; s['played_loss']=(1-s.win)*s.played
entries=s.groupby(['player_id','player_name','year','tourney_id','tourney_name','surface'],dropna=False).agg(age=('player_age','first'),rank=('player_rank','first'),recorded_matches=('match_id','size'),played_matches=('played','sum'),wins=('played_win','sum'),losses=('played_loss','sum'),furthest_round=('stage','max'),title=('slam_title','max')).reset_index(); entries['result']=np.where(entries.title,'W',entries.furthest_round.map({v:k for k,v in rounds.items()})); entries.to_csv(out/'slam_entries.csv',index=False)
def summarize(a,keys):
 a=a.copy(); a['played_win']=a.win*a.played; a['played_loss']=(1-a.win)*a.played; valid=a.status.eq('completed') & a.svpt.gt(0) & a.ace.notna(); a['ace_num']=a.ace.where(valid); a['ace_den']=a.svpt.where(valid); valid2=a.status.eq('completed') & a.svpt.gt(0)&a['1stWon'].notna()&a['2ndWon'].notna(); a['serve_won']=(a['1stWon']+a['2ndWon']).where(valid2); a['serve_den']=a.svpt.where(valid2)
 g=a.groupby(keys,dropna=False).agg(recorded_matches=('match_id','size'),played_matches=('played','sum'),wins=('played_win','sum'),losses=('played_loss','sum'),slam_titles=('slam_title','sum'),age_mean=('player_age','mean'),rank_mean=('player_rank','mean'),ace_matches=('ace_num','count'),aces=('ace_num','sum'),ace_service_points=('ace_den','sum'),serve_matches=('serve_won','count'),service_points_won=('serve_won','sum'),service_points=('serve_den','sum')).reset_index(); g['win_rate']=g.wins/g.played_matches.replace(0,np.nan); g['ace_rate']=g.aces/g.ace_service_points.replace(0,np.nan); g['serve_win_rate']=g.service_points_won/g.service_points.replace(0,np.nan); return g
annual=summarize(p,['player_id','player_name','year']); sa=summarize(s,['player_id','player_name','year']); sa=sa[['player_id','year','played_matches','wins','losses','win_rate','slam_titles']].rename(columns={c:'slam_'+c for c in ['played_matches','wins','losses','win_rate']}); annual=annual.drop(columns='slam_titles').merge(sa,on=['player_id','year'],how='left'); annual=annual.merge(entries.groupby(['player_id','year']).size().rename('slam_entries').reset_index(),on=['player_id','year'],how='left');
for c in ['slam_played_matches','slam_wins','slam_losses','slam_titles','slam_entries']: annual[c]=annual[c].fillna(0).astype(int)
annual.to_csv(out/'player_year.csv',index=False)
# age from actual tournament age, floor to completed age
p['age_year']=np.floor(p.player_age); age=summarize(p.dropna(subset=['age_year']),['player_id','player_name','age_year']); age.to_csv(out/'player_age.csv',index=False)
surf=summarize(s,['player_id','player_name','surface']); surf=surf.merge(entries.groupby(['player_id','surface'],dropna=False).size().rename('slam_entries').reset_index(),on=['player_id','surface'],how='left'); surf['title_per_entry']=surf.slam_titles/surf.slam_entries; surf.to_csv(out/'slam_surface.csv',index=False)
r=sub[sub.winner_id.isin(ids)&sub.loser_id.isin(ids)].copy(); r.to_csv(out/'rivalry_matches.csv',index=False)
rows=[]
for a,b in combinations(ids,2):
 x=r[((r.winner_id==a)&(r.loser_id==b))|((r.winner_id==b)&(r.loser_id==a))];
 for scope,t in [('all',x),('slam',x[x.slam])]:
  t=t[t.played]; rows.append(dict(player_a=ids[a],player_b=ids[b],scope=scope,matches=len(t),a_wins=int((t.winner_id==a).sum()),b_wins=int((t.winner_id==b).sum())))
pd.DataFrame(rows).to_csv(out/'rivalry_summary.csv',index=False)
f=d[d.title].copy(); f[['year','tourney_id','tourney_name','surface','winner_id','winner_name','winner_age','loser_name','score','status']].to_csv(out/'all_slam_finals.csv',index=False)
summary=annual.groupby(['player_id','player_name']).agg(first_year=('year','min'),last_year=('year','max'),played_matches=('played_matches','sum'),wins=('wins','sum'),slam_entries=('slam_entries','sum'),slam_titles=('slam_titles','sum')).reset_index(); summary['win_rate']=summary.wins/summary.played_matches
for i,row in summary.iterrows():
 t=annual[annual.player_id==row.player_id].set_index('year').slam_titles.reindex(range(1968,2025),fill_value=0); roll=t.rolling(3).sum(); peak=roll.max(); summary.loc[i,'peak_3yr_titles']=peak; summary.loc[i,'peak_windows']='; '.join(f'{y-2}-{y}' for y in roll[roll.eq(peak)].index); f1=f[f.winner_id==row.player_id].sort_values('date'); summary.loc[i,'first_title_age']=f1.winner_age.iloc[0]; summary.loc[i,'last_title_age']=f1.winner_age.iloc[-1]
summary.to_csv(out/'player_summary.csv',index=False)
quality=pd.DataFrame({'field':sub.columns,'missing_count':sub.isna().sum().values,'missing_pct':sub.isna().mean().values*100}); quality.to_csv(out/'missingness.csv',index=False)
print('raw',len(d),'selected',len(sub),'slams',len(s.drop_duplicates('match_id')),'player rows',len(p),'entries',len(entries),'annual',len(annual),'rivalry',len(r)); print(sub.status.value_counts()); print(summary.to_string(index=False)); print(quality[quality.field.isin(['winner_age','winner_rank','minutes','w_ace','w_svpt'])].to_string(index=False)); print('dates',d.date.isna().sum(),'dup',d.match_id.duplicated().sum())
# full matrix: absent seasons are not zeros; active seasons with no title are zeros
matrix=pd.MultiIndex.from_product([list(ids),range(1986,2025)],names=['player_id','year']).to_frame(index=False).merge(annual.drop(columns='player_name'),on=['player_id','year'],how='left'); matrix.insert(1,'player_name',matrix.player_id.map(ids)); matrix['observed_season']=matrix.recorded_matches.notna(); matrix['slam_participation']=np.where(~matrix.observed_season,'no_tour_record',np.where(matrix.slam_entries.fillna(0).gt(0),'slam_entry','no_slam_entry')); matrix.to_csv(out/'player_year_matrix.csv',index=False)
s['age_year']=np.floor(s.player_age); summarize(s.dropna(subset=['age_year']),['player_id','player_name','age_year']).to_csv(out/'slam_player_age.csv',index=False)
assert summary.slam_titles.sum()==94
assert len(sub)==6764 and len(p)==6995
assert (summary.slam_titles<=summary.slam_entries).all()
