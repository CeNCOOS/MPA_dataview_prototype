## The California Current Merged satellite-derived 4km dataset ##

This data is a developed and maintained by Mati Kahru of UCSD-SIO.
[More information is available here](http://www.wimsoft.com/CC4km.htm)

``` 4-km Merged Chlorophyll-a ``` Daily Chl-a values are calculated from all available satellites sensing reflectance using algorithms optimized for the California Current. The different source are merged into a single 4km resolution dataset. From their website (accessed on 2019-7-11):

> Therefore we currently merge data from 4 sensors: MODISA, VIIRS-SNNP (both Calfit2015), OLCI-A (OC4ME, since 2017) and the transformed VIIRS-SNPP1 (since 2017). Data from OLCI-B are being evaluated and will will be included at a later time.


Data are pulled from the winsoft website using a shell script called `pull_mergedCHL.sh`

Data files are stored as daily HDF4 files, which are on a grid of 540(w) x 417(h) with approximately 4km step. The __upper-left corner = (45N, -140E)__. the __lower-right corner is (30.03597N, -115.5454E)__

 Pixel values of 1 correspond to the coastline, pixel values of 255 (white) are considered missing data or land mask.


## Converting to NetCDF ##

After data are downloaded, run the `merge_chl_files.py` and `merge_npp_files.py`. This script will convert the pixel values into proper scientific units and out put a single netcdf file for each year.
