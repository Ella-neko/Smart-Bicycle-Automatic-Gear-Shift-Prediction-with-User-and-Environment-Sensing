資料放在 data\can_Internal_difference\static_IMU\multiprocess

以日期為檔案名稱的(0424、0609_out)為樹梅派與Arduino原始檔
TEST_0609.TXT 為Arduino原始檔
2021691119output.csv 為樹梅派原始檔

after_pv2.csv 為經過dataprocess_v3.py 處理後

after_GS_skip_freetime.csv 為經過gear_smooth.py與OSM_test.py處理後

前處理流程 :   dataprocess_v3.py(生成after_pv2.csv )
	     ->gear_smooth.py(生成after_GS_skip_freetime.csv )
	     ->OSM_test.py(生成after_GS_skip_freetime.csv )

mix資料夾內為處理過後的資料
after_OSM_0515.csv 為校內50,000筆的校內訓練資料，較前面的日期為較少的資料量
outside_0610.csv 為校外50,000筆的校內訓練資料，較前面的日期為較少的資料量

outside_test_0604.csv 為校外2576筆測試資料
test_0521_2000.csv 為校內2000筆測試資料

mix/sub 內為所有經過前處理的資料(按照日期放置)

time_save 內為有時間資訊(日期與時間)的資料，用於雲端資料庫上傳用(網頁的上傳部分)


