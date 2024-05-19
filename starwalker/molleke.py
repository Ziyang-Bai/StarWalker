import xarray as xr


nc_file_path = 'E:\\Windows\\download\\VNP02DNB_NRT.A2024132.2254.002.2024133021143.nc'


# 使用xarray打开NC文件
ds = xr.open_dataset(nc_file_path)

# 获取并打印所有变量名
variable_names = list(ds.data_vars.keys())
print("变量名如下：", variable_names)