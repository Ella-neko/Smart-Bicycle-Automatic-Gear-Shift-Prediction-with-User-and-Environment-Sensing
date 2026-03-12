環境建置(win10)
	1. 安裝anaconda:https://www.anaconda.com/products/individual
	1. 使用anaconda建立一python3.6環境
	2. 在該環境安裝 CMD.exe Prompt、Spyder
	3. pip install numpy 
	4. pip install pandas
	5. pip install matplotlib
	6. pip install OSMPythonTools 	(OSM_test.py用)
	7. pip install torch 		(ANN.py用)
	8. pip install torchcontrib	(ANN.py用)
	9. pip install sklearn
	10. pip install xgboost
	11. pip install lightgbm
	12. pip install deep-forest
	13. pip install catboost

	
test_muti_thread( Arduino )
啟動流程:
	1. 馬達交流電源開啟
	2. USB 接上電源
	3. 聽到馬達初始化的運轉聲，按鈕版上的藍燈熄滅(成功啟動)
		3.1 若藍燈不滅為初始化出現錯誤，可將USB接上PC開啟IDE查看
		3.2 若藍燈交替閃爍為SD卡初始化錯誤，可將SD卡相關接口(對接線從插、SD從插)重新插拔

PT_WAIT_UNTIL(pt, millis() - lastTimeBlinkMotor > 300); //300為控制感測器的採樣頻率(300ms)，可於各個排程副程式進行設定
若時間無法透過RTCsetup()校正RTC模組的電池應該是沒電了，可以整組RTC進行更換(有備份2組)
**資料儲存於SD卡中，需插到PC上進行讀取

RPI
啟動流程:
	1. USB接上電源，行動網路開啟
	2. 使用RPI_SSH.jpg的資訊利用SSH連接至樹梅派(連接端與樹梅派需連接相同的網路)(若不是使用行動wifi分享器提供的網路IP會有不同，需連接至螢幕查詢IP)
	3. cd Desktop/RF_multi_system\(0610\)/ 
	4. python RasPi_only_gps.py
**資料儲存於output資料夾內，根據日期進行儲存ex:20213412351output.csv(2021/3/4 12:35:01)

PC
資料前處理
	1. dataprocess_v3.py
		d = open('data/can_Internal_difference/static_IMU/multiprocess/0609_out/202169175920output_3.csv', 'r') //樹梅派收集的資料
		f = open('data/can_Internal_difference/static_IMU/multiprocess/0609_out/TEST_0609_3.TXT', 'r') //Arduino 收集的資料
		time_step //設定sensor data間隔
		np.savetxt('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_pv2_3_timesave.csv',final_data, delimiter=',',header="lati,long,Gyro,Gear,Rate,Pressure,Heartbeat,Temp,Time",comments='') //資料儲存
	2. gear_smooth.py
		df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_pv2_3_timesave.csv') //讀取經過dataprocess_v3後的資料
		after_smooth.to_csv('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_GS_skip_freetime_3.csv', index = False) //資料儲存
	3. OSM_test.py
		df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_GS_skip_freetime_3.csv') //讀取經過gear_smooth後的資料
		if(j%1000==0):
			result = overpass.query('node["highway"= "crossing"](around:5000,'+str(df['lati'][j])+', '+str(df['long'][j])+');out;') //5000為設定OSM讀取的範圍並且1000個sample讀取一次
		if((abs(result.elements()[i].lat()-df['lati'][j])**2 + abs(result.elements()[i].lon()-df['long'][j])**2)**0.5<0.0005): //設定要考慮的範圍，0.0005大約為50公尺
		df.to_csv('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_GS_skip_freetime_3.csv', index = False) //儲存資料

預測
	1. ANN.py
		df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/after_OSM_0513.csv') //訓練資料
		df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/test_0513.csv') //測試資料
		gear_num //設定past gear要加入的次數(數字越大past gear的權重相對越高)
		model = TabularModel( conts.shape[1], 6, [20,20,40,40,80,40,40,20,20], p=0.2) //[20,20,40,40,80,40,40,20,20]設定每一層的節點數，p為dropup，6為類別數
		lr //設定learning rate
		epochs = 10 //迴圈次數
	2. RF.py
		df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/after_OSM_0513.csv') //訓練資料
		df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/test_0513.csv') //測試資料
		for i in range(19)://用於稀釋past gear的權重，數字越大past gear權重越低(104行)
		tp //設定使用的訓練資料量(0~1)
		for i in range(80) ://兩階段訓練的次數(181行)
		clf=RandomForestClassifier(n_estimators=70,min_samples_leaf = 6) //生成RF分類器(162行)
		clf2=RandomForestClassifier(n_estimators=0,max_depth=11,min_samples_leaf = 6,warm_start=1) //生成RF分類器2(166行)
		#------RF-----------------------------------
		#------RF END-----------------------------------//這兩行中間為Random Forests

		model = CascadeForestClassifier(n_estimators=5,random_state=1,n_jobs=8,n_tolerant_rounds =2,n_trees=70,max_depth=3,min_samples_leaf = 4) //生成DF分類器(222行)
		#-----------Deep Forest------------------------
		#-----------Deep Forest END------------------------//這兩行中間為Deep Forest
		DF、RF兩者擇一執行
	3. XGBoost.py
		df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/after_OSM_0513.csv') //訓練資料
		df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/test_0513.csv') //測試資料
		tp //設定使用的訓練資料量(0~1)
		clf1 = xgb.XGBClassifier(n_jobs=-1,n_estimators =1000,tree_method='hist') //生成XGB分類器(264行)
		clf2 = xgb.XGBClassifier(n_jobs=-1,
                         n_estimators =1,
                         tree_method='gpu_hist',
                         predictor='gpu_predictor',
                         max_depth=3,
                         min_child_weight = 4,
                         gamma=0.2,
                         subsample=0.8,
                         colsample_bytree=0.8,
                         learning_rate=0.1,
                         ) //生成分類器2(270行)

		for i in range(80): //兩階段訓練的次數(290行)
	4. XGBoost_v2.py (CAtBoost、LightGBM)
		df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/after_OSM_0513.csv') //訓練資料
		df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/test_0513.csv') //測試資料
		tp //設定使用的訓練資料量(0~1)
		clf = CatBoostClassifier(iterations=1000, 
                           learning_rate=0.1,
                           depth=3,
                           loss_function='MultiClass') //生成CATBoost分類器(197行)
		clf2 = CatBoostClassifier(iterations=10,
                           learning_rate=0.1,
                           depth=3,
                           loss_function='MultiClass') //生成CATBoost分類器2(201行)
		#-------------------------------------------------catboost-----------------------------------------------
		#-------------------------------------------------catboost end-----------------------------------------------//這兩行中間為catboost 
		
		clf1 = lgb.LGBMClassifier(objective="multiclass") //生成LGBM分類器(263行)
		clf2 = lgb.LGBMClassifier(objective="multiclass",n_estimators=200,max_depth=3,min_child_samples=5) //生成LGBM分類器(267行)
		#---------------------------lightGBM---------------------------------------------------
		#---------------------------lightGBM end---------------------------------------------------//這兩行中間為LGBM
		CATBoost、LGBM兩者擇一執行