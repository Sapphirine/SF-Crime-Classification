import pandas as pd
import numpy as np
import zipfile
import matplotlib.pyplot as pl
import seaborn as sns
from datetime import datetime

# Supplied map bounding box:
#    ll.lon     ll.lat   ur.lon     ur.lat
#    -122.52469 37.69862 -122.33663 37.82986
mapdata = np.loadtxt("sf_map_copyright_openstreetmap_contributors.txt")
asp = mapdata.shape[0] * 1.0 / mapdata.shape[1]

lon_lat_box = (-122.5247, -122.3366, 37.699, 37.8299)
clipsize = [[-122.5247, -122.3366],[ 37.699, 37.8299]]

train = pd.read_csv('train.csv')

#Get rid of the bad lat/longs
train['Xok'] = train[train.X<-121].X
train['Yok'] = train[train.Y<40].Y
train = train.dropna()

# 1. All Training Set: 39
train['Dates'] = pd.to_datetime(train['Dates'])
train['Year']  = pd.DatetimeIndex(train['Dates']).year
train['Month'] = pd.DatetimeIndex(train['Dates']).month
train['Day']   = pd.DatetimeIndex(train['Dates']).day
train['Hour']  = pd.DatetimeIndex(train['Dates']).hour
categories = sorted(train["Category"].unique())
month = sorted(train["Month"].unique())
hour = sorted(train["Hour"].unique())
C_counts   = train.groupby(["Category"]).size()
print C_counts

for category in categories:
	pl.figure(figsize=(20,20*asp))
	trainc = train[train.Category == category]
	ax = sns.kdeplot(trainc.Xok, trainc.Yok, clip=clipsize, aspect=1/asp,n_levels=25,cmap="Reds_d")
	ax.imshow(mapdata, cmap=pl.get_cmap('gray'), 
              extent=lon_lat_box, 
              aspect=asp)
	ax.figure.suptitle(category, fontsize = 20)
	string = category.split("/")[0]
	pl.savefig(string + '.png')
	pl.close('all')


# 2. Every Year : 39 * 12
for category in categories:
	for i in range(2003,2016):
		pl.figure(figsize=(20,20*asp))
		start  = str(i) + '-01-01 00:00:00'
		end    = str(i) + '-12-31 23:59:59'		
		trainc = train[train.Category == category]
		traind = trainc.loc[(trainc.Dates > start)&(trainc.Dates < end)]
		# traind = trainc.loc[trainc.Dates > '2015-01-01 00:00:00']
		if traind.empty or traind.groupby(["Category"]).size().item() <=1 :
			print i
			print "EMPTY Category: %s" % category
			continue
		try:
			ax = sns.kdeplot(traind.Xok, traind.Yok, clip=clipsize, aspect=1/asp, n_levels=10, cmap="Reds_d")
			ax.imshow(mapdata, cmap=pl.get_cmap('gray'), 
              	extent=lon_lat_box, 
              	aspect=asp)
			string = category.split("/")[0]
			pl.savefig(string + '_'+ str(i) + '.png')
			pl.close('all')
		except ValueError: 
			pass




# 3. Every Month :  12 * 39 bar
for category in categories:
	trainc = train[train.Category == category]
	mc     = trainc.groupby(["Month"]).size()
	mn_sz  = mc.max()/4
	for i in range(2003,2016):
		start  = str(i) + '-01-01 00:00:00'
		end    = str(i) + '-12-31 23:59:59'
		trainc = train[train.Category == category]	
		traind = trainc.loc[(trainc.Dates > start)&(trainc.Dates < end)]
		# if traind.empty or traind.groupby(["Category"]).size().item() <=1 :
		# 	print i
		# 	print "EMPTY Category: %s" % category
		# 	continue
		try:
			mon_count = traind.groupby(["Month"]).size()
			df     = pd.DataFrame(mon_count, index = month,columns=['Number'])
			mon_df = df.fillna(0)
			ax     = sns.barplot(x=month, y=mon_df['Number']);
			string = category.split("/")[0]
			ax.figure.suptitle("Month Distribution of "+string+" (Year: " + str(i)+")", fontsize = 10)
			pl.ylim(0,mn_sz)
			pl.ylabel('Number of Crimes', fontsize=10)
			pl.xlabel('Month', fontsize=10)
			pl.savefig(string+'_'+str(i) + '.png')
			pl.close('all')
		except: 
			pass


# 4. Every Day : 12 * 39 wave
for category in categories:
	trainc = train[train.Category == category]
	hr     = trainc.groupby(["Hour"]).size()
	hr_sz  = hr.max()/5
	for i in range(2003,2015):
		start  = str(i) + '-01-01 00:00:00'
		end    = str(i) + '-12-31 23:59:59'
		trainc = train[train.Category == category]	
		traind = trainc.loc[(trainc.Dates > start)&(trainc.Dates < end)]
		# if traind.empty or traind.groupby(["Category"]).size().item() <=1 :
		# 	print i
		# 	print "EMPTY Category: %s" % category
		# 	continue
		try:
			hr_count = traind.groupby(["Hour"]).size()
			df     = pd.DataFrame(hr_count, index = hour,columns = ['Number'])
			hr_df  = df.fillna(0)
			ax     = sns.barplot(x=hour, y=hr_df['Number']);
			string = category.split("/")[0]
			ax.figure.suptitle("Hour Distribution of "+string+" (Year: " + str(i)+")", fontsize = 10)
			pl.ylim(0,hr_sz)
			pl.ylabel('Number of Crimes', fontsize=10)
			pl.xlabel('Hour', fontsize=10)
			pl.savefig(string + '_' + str(i) + '.png')
			pl.close('all')
		except: 
			pass


