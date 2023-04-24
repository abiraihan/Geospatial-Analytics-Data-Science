
import os
import json
import fiona
import shutil
import pyproj
import shapely
import tempfile
import requests
import rasterio
import geopandas as gpd
from rasterio.plot import show
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, shape
from geoanalytics.reporting.assets.colorscheme import Colorbar
from geoanalytics.graphs.plots.plots import Plots
from geoanalytics.reporting.build.reports import Report
import warnings
from shapely import speedups
warnings.filterwarnings("ignore")
speedups.disable()

class Basemap:
    
    @classmethod
    def Extent(
            cls,
            filepaths,
            credential:str, 
            **kwargs
            ):
        
        """

        Parameters
        ----------
        filepaths : string
            - shapefile path location
        **kwargs : Keyword args
            - Padding size, height and width increase

        Returns
        -------
        dict
        - Keys:
            'box': Bounding box as list item,
            'bounds': Bounding box as tuple,
            'crs': Coordinate Reference System,
            'height': Pixel number for image height,
            'width': Pixel number for image width and
            'geometry': Source geometry as shapely geometry

        """
                
        cls.filepaths = filepaths
        cls.credential = credential
        
        credentials = json.load(open(cls.credential))
        
        size_args = dict(
            ratio = 1,
            padding = None
            )
        
        for key, value in size_args.items():
            if key in kwargs:
                size_args[key] = kwargs[key]
        
        def image_ratio(ratio):
            if 0 < ratio <= 1:
                if int(1280*ratio) <= 1280:
                    return int(1280*ratio)
                else:
                    raise ValueError("Check Input Values for Image ration")
            else:
                if ratio < 0:
                    raise ValueError("ratio Value cannot be less than 0")
                else:
                    raise ValueError("ratio Value cannot be more than 1")
        
        projection = lambda geog, proj : pyproj.Transformer.from_crs(
            crs_from=pyproj.CRS.from_user_input(geog),
            crs_to=pyproj.CRS.from_user_input(proj),
            always_xy=True
            ).transform
        
        file = fiona.open(cls.filepaths, 'r')
        file_crs = file.crs
        target_crs = int(file.crs['init'].split(':')[1])
        if len(file) > 1:
            polys = shapely.ops.unary_union([shape(i['geometry']) for i in file])
        else:
            polys = shape(file[0]['geometry'])
        # print(polys.area*1e10)
        file.close()
        proj_polys = shapely.ops.transform(
            projection(target_crs, 3857),
            polys)
        # print(proj_polys.area)
        
        xmin, ymin, xmax, ymax = proj_polys.bounds
        
        width = shapely.geometry.LineString(
            (shapely.geometry.Point(xmax, ymax),
              shapely.geometry.Point(xmin, ymax))
            )
        height = shapely.geometry.LineString(
            (shapely.geometry.Point(xmin, ymax),
              shapely.geometry.Point(xmin, ymin))
            )
        
        height_px = image_ratio(size_args['ratio'])
        width_px = 1280
        
        width_inc = ((ymax - ymin)/ height_px)*width_px - width.length
        height_inc = ((xmax - xmin)/ width_px)*height_px - height.length
        
        if width_inc > 0:
            xmax = xmax + width_inc/2
            xmin = xmin - width_inc/2
        else:
            ymax = ymax + (height_inc/2)
            ymin = ymin - (height_inc/2)
        
        width_length = shapely.geometry.LineString(
            (shapely.geometry.Point(xmax, ymax),
             shapely.geometry.Point(xmin, ymax))
            ).length
        
        height_length = shapely.geometry.LineString(
            (shapely.geometry.Point(xmin, ymax),
             shapely.geometry.Point(xmin, ymin))
            ).length
        
        # print(width.length, height.length)
        if size_args['padding'] is not None:
            xmax = xmax + ((width_length/2)*size_args['padding'])/100
            xmin = xmin - ((width_length/2)*size_args['padding'])/100
            ymax = ymax + ((height_length/2)*size_args['padding'])/100
            ymin = ymin - ((height_length/2)*size_args['padding'])/100
        
        bounds_poly = Polygon([
            (xmin, ymin),
            (xmin, ymax),
            (xmax, ymax),
            (xmax, ymin)
            ])
        oriented_poly = shapely.geometry.polygon.orient(
            bounds_poly,
            sign = 1.0
            )
        assert oriented_poly.is_valid, 'Not a valid geometry, check def Extent at assert args'
                
        trans_polys = shapely.ops.transform(
            projection(3857, target_crs),
            oriented_poly)
        
        urls = f"https://api.mapbox.com/styles/v1/mapbox/{credentials['styles']}/static/{list(trans_polys.bounds)}/{width_px}x{height_px}@2x?access_token={credentials['token']}&attribution=false&logo=false"
        
        basenames = os.path.basename(cls.filepaths).split('.', 1)[0]
        temp_dir = tempfile.mkdtemp()
        temp_png = os.path.join(temp_dir, f"{basenames}.png")
        temp_tif = os.path.join(temp_dir, f"{basenames}.tif")
        
        response = requests.get(urls)
        if response.status_code == 200:
            with open(temp_png, 'wb') as f:
                f.write(response.content)
        else:
            print(f"Found Error while getting image data, status code : {response.status_code}")
        
        datasets = rasterio.open(temp_png, 'r')
        bands = [1, 2, 3]
        data = datasets.read(bands)
        # print(data.shape)
        transform = rasterio.transform.from_bounds(
            *trans_polys.bounds,
            data.shape[1],
            data.shape[2]
            )
        assert os.path.exists(temp_png), "PNG File does not exist"
        with rasterio.open(
                temp_tif, 'w',
                driver = 'GTiff',
                width = data.shape[1],
                height = data.shape[2],
                count = data.shape[0],
                dtype = data.dtype,
                nodata = 0,
                transform = transform,
                crs = file_crs
                ) as dst:
            dst.write(data, indexes = bands)
        os.remove(temp_png)
        assert os.path.exists(temp_tif), "GeoTiff File does not exists"
        return {'box' : list(trans_polys.bounds),
                'bounds' : trans_polys.bounds,
                'crs' :  file_crs,
                'width' : width_px,
                'height' : height_px,
                'geometry': polys,
                'urls': urls,
                'temp_dir': temp_dir,
                'basenames': basenames,
                'filepath': cls.filepaths,
                'temp_tif': temp_tif
                }
    
    @staticmethod
    def Boundary(extent_info, outpath, **kwargs):
        
        args = dict(
            image_border_width = 2,
            image_border_color = 'black',
            facecolor = 'grey',
            edgecolor = 'black',
            linewidth = 0.7,
            alpha = 0.7,
            figsize = (10, 10),
            dpi = 300,
            transparent = True,
            bbox_inches = 'tight',
            pad_inches = 0.00
            )
        
        for key, value in args.items():
            if key in kwargs:
                args[key] = kwargs[key]
                
        fields = gpd.read_file(extent_info['filepath'])
        
        basemaps = rasterio.open(extent_info['temp_tif'])
        extent_info.pop('temp_tif')
        
        png_image_path = os.path.join(outpath, f"{extent_info['basenames']}.png")
        
        fig, ax = plt.subplots()
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(args['image_border_width'])
            ax.spines[axis].set_color(args['image_border_color'])
        plt.tick_params(
            left = False,
            right = False,
            labelleft = False,
            labelbottom = False,
            bottom = False
            )
        plt.tight_layout()
        ax = show(
            basemaps,
            extent = [
                basemaps.bounds[0],
                basemaps.bounds[2],
                basemaps.bounds[1],
                basemaps.bounds[3]
                ],
            ax = ax
            )
        
        fields.plot(
            ax = ax,
            facecolor = args['facecolor'],
            edgecolor = args['edgecolor'],
            linewidth = args['linewidth'],
            alpha = args['alpha'],
            figsize = args['figsize']
            )
        try:
            plt.savefig(
                png_image_path,
                dpi = args['dpi'],
                transparent = args['transparent'],
                bbox_inches = args['bbox_inches'],
                pad_inches = args['pad_inches']
                )
        finally:
            shutil.rmtree(extent_info['temp_dir'])
            extent_info.pop('temp_dir')
        
        extent_info[extent_info['basenames']] = {
                'map': png_image_path
                }
        extent_info['plot_type'] =  'Boundary Plot'
        return extent_info
    
    @staticmethod
    def Rxmap(extent_info, outpath, **kwargs):
        
        args = dict(
            target_rate_attr = 'Tgt_Rate',
            image_border_width = 2,
            image_border_color = 'black',
            edgecolor = 'black',
            linewidth = 0.7,
            alpha = 0.5,
            figsize = (10, 10),
            dpi = 300,
            transparent = True,
            bbox_inches = 'tight',
            pad_inches = 0.00
            )
        
        for key, value in args.items():
            if key in kwargs:
                args[key] = kwargs[key]
        
        png_rxmap_path = os.path.join(outpath, f"{extent_info['basenames']}.png")
        legend_path = os.path.join(outpath, f"{extent_info['basenames']}_legend.png")
        fields = gpd.read_file(extent_info['filepath'])
        sorted_target_val = sorted(fields[args['target_rate_attr']].unique().tolist())
        cmaps = Colorbar.Legend(sorted_target_val, colorbar_filepath = legend_path)
        basemaps = rasterio.open(extent_info['temp_tif'])
        extent_info.pop('temp_tif')
        
        fig, ax = plt.subplots()
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(args['image_border_width'])
            ax.spines[axis].set_color(args['image_border_color'])
        plt.tick_params(
            left = False,
            right = False,
            labelleft = False,
            labelbottom = False,
            bottom = False
            )
        plt.tight_layout()
        ax = show(
            basemaps,
            extent = [
                basemaps.bounds[0],
                basemaps.bounds[2],
                basemaps.bounds[1],
                basemaps.bounds[3]
                ],
            ax = ax
            )
        
        fields.plot(
            ax = ax,
            column = args['target_rate_attr'],
            cmap = cmaps,
            legend = False,
            edgecolor = args['edgecolor'],
            linewidth = args['linewidth'],
            alpha = args['alpha'],
            figsize = args['figsize']
            )
        try:
            plt.savefig(
                png_rxmap_path,
                dpi = args['dpi'],
                transparent = args['transparent'],
                bbox_inches = args['bbox_inches'],
                pad_inches = args['pad_inches']
                )
        finally:
            shutil.rmtree(extent_info['temp_dir'])
            extent_info.pop('temp_dir')
        
        extent_info[extent_info['basenames']] = {
                'legend': legend_path,
                'map': png_rxmap_path
                }
        extent_info['plot_type'] =  'Rx Map Plot'
        return extent_info
    
    @staticmethod
    def PlantingVarietySwaths(filepaths, credentials, *attributes, **kwargs):
        
        args = dict(
            ratio = 1,
            padding = 10,
            target_attr = 'Product',
            xaxis_length_attr = 'Swth_Wdth_', # Swath length
            yaxis_length_attr = 'Distance_f', # Distance
            rotation_attr = 'Track_deg_', #Rotation
            data_type = 'Planting'
            )
        
        for key, value in args.items():
            if key in kwargs:
                args[key] = kwargs[key]
        
        data = Report.PolyPlantingVariety(
            filepaths, *attributes,
            data_type = args['data_type'],
            target_attr = args['target_attr'],
            xaxis_length_attr = args['xaxis_length_attr'], 
            yaxis_length_attr = args['yaxis_length_attr'], # Distance
            rotation_attr = args['rotation_attr'], #Rotation
            ) # args =  ['Grower___N', 'Farm___Nam', 'Field___Na', 'Product___']
        extent_info = Basemap.Extent(
            data['swath_filepath'],
            credentials,
            ratio = args['ratio'],
            padding = args['padding']
            )
        
        extent_info.update(data)
        extent_info['data_type'] = args['data_type']
        extent_info['target_attr'] = args['target_attr']
        extent_info['plot_type'] =  'Planting Variety Plot'
        return extent_info
    
    @staticmethod
    def PlantingVarietyMap(extent_info, outpath, **kwargs):
        
        # usage: extent_info = PlantingVarietySwaths(
        # plantfiles, creds, *['Grower___N', 'Farm___Nam', 'Field___Na', 'Product___']
        # )
        # df = PlantingVarietyMap(extent_info, outpath)
                
        args = dict(
            target_attr = 'Product',
            num_variety = 9,
            png_filepath = os.path.join(outpath, f"{extent_info['basenames']}_legend.png"),
            plant_varietymap_path = os.path.join(outpath, f"{extent_info['basenames']}.png"),
            font_name = 'Avenir LT Std 65 Medium Oblique',
            plt_margin = 0.0,
            font_size = 12,
            font_style = 'oblique',
            width = 2,
            height = 0.16,
            alpha = 1,
            pad = 4,
            font_length_limit = 11,
            variety_font_size = 10,
            auto_font_dicts = {'start': 9, 'stop': 30, 'interval': 5},
            dpi = 300,
            color = 'tab20',
            transparent = True,
            bbox_inches = 'tight',
            pad_inches = 0.00,
            image_border_width = 2,
            image_border_color = 'black',
            figsize = (10, 10),
            frameon = False,
            markerscale = 1.5,
            markerfirst =  True,
            alignment = 'left',
            labelspacing = 0.4,
            framealpha = 1,
            handlelength = 0.3,
            handleheight = 0.0,
            borderaxespad = 0.1
            )
        
        for key, value in args.items():
            if key in kwargs:
                args[key] = kwargs[key]
        
        extent_info[extent_info['basenames']] = {
                'legend': args['png_filepath'],
                'map': args['plant_varietymap_path']
                }
        
        legends = Plots.PlantingVarietyLegend(
            extent_info['asplanted_variety'],
            **args
            )
        extent_info['type'] = legends['type']
        
        fields = gpd.read_file(extent_info['swath_filepath'])
        
        basemaps = rasterio.open(extent_info['temp_tif'])
        extent_info.pop('temp_tif')
        
        fig, ax = plt.subplots()
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(args['image_border_width'])
            ax.spines[axis].set_color(args['image_border_color'])
        plt.tick_params(
            left = False,
            right = False,
            labelleft = False,
            labelbottom = False,
            bottom = False
            )
        plt.tight_layout()
        ax = show(
            basemaps,
            extent = [
                basemaps.bounds[0],
                basemaps.bounds[2],
                basemaps.bounds[1],
                basemaps.bounds[3]
                ],
            ax = ax
            )
        
        for colors, variety in fields.groupby(args["target_attr"]):
            variety.plot(
                ax = ax,
                color = legends['cmaps_vals'][colors],
                legend = False,
                figsize = args['figsize']
                )
        
        try:
            plt.savefig(
                args['plant_varietymap_path'],
                dpi = args['dpi'],
                transparent = args['transparent'],
                bbox_inches = args['bbox_inches'],
                pad_inches = args['pad_inches']
                )
        finally:
            shutil.rmtree(extent_info['temp_dir'])
            extent_info.pop('temp_dir')
            shutil.rmtree(os.path.dirname(extent_info['swath_filepath']))
            extent_info.pop('swath_filepath')
        
        return extent_info
    
    @staticmethod
    def PlantingRateSwaths(filepath, credentials, *args, **kwargs):
        
        rate_args = dict(
            ratio = 1,
            padding = 10,
            target_attr = 'Rt_Apd_Ct_',
            xaxis_length_attr = 'Swth_Wdth_', # Swath length
            yaxis_length_attr = 'Distance_f', # Distance
            rotation_attr = 'Track_deg_', #Rotation
            data_type = 'Planting'
            )
        
        for key, value in rate_args.items():
            if key in kwargs:
                rate_args[key] = kwargs[key]
        
        data = Report.PolyPlantingRate(
            filepath,
            *args, **rate_args
            )
        
        extent_info = Basemap.Extent(
            data['swath_filepath'],
            credentials,
            **rate_args
            )
        
        extent_info.update(data)
        extent_info['data_type'] = rate_args['data_type']
        extent_info['target_attr'] = rate_args['target_attr']
        
        return extent_info
    
    @staticmethod
    def PlantingRateMap(extent_info, outpath, **kwargs):
        
        args = dict(
            bar_legend_filepath = os.path.join(outpath, f"{extent_info['basenames']}_bar_legend.png"),
            cmaps_legend_filepath = os.path.join(outpath, f"{extent_info['basenames']}_cmap_legend.png"),
            font_name = 'Avenir LT Std 55 Oblique',
            image_border_width = 2,
            image_border_color = 'black',
            mapsWidth = 10,
            mapsHeight = 10,
            font_size = 14,
            font_style = 'oblique',
            plt_margin = 0.0,
            width = 12,
            bar_height = 0.2,
            cmaps_height = 0.2,
            alpha = 0.9,
            pad = 0,
            bar_label_box_width = 0.97,
            cmaps_label_box_width = 1.0,
            bar_color = 'grey',
            cmaps_color = 'RdYlGn',
            dpi = 300,
            transparent = True,
            bbox_inches = 'tight',
            pad_inches = 0.00
            )
        
        for key, value in args.items():
            if key in kwargs:
                args[key] = kwargs[key]
           
        planting_ratemap_path = os.path.join(outpath, f"{extent_info['basenames']}.png")
        
        legends = Plots.PlantingRateLegend(extent_info['rates_data'], **args)
        
        extent_info[extent_info['basenames']] = {
                'bar_legend': args['bar_legend_filepath'],
                'cmaps_legend': args['cmaps_legend_filepath'],
                'map': planting_ratemap_path
                }
        
        fields = gpd.read_file(extent_info['swath_filepath'])
        
        basemaps = rasterio.open(extent_info['temp_tif'])
        extent_info.pop('temp_tif')
        
        import matplotlib
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(args['image_border_width'])
            ax.spines[axis].set_color(args['image_border_color'])
        plt.tick_params(
            left = False,
            right = False,
            labelleft = False,
            labelbottom = False,
            bottom = False
            )
        plt.tight_layout()
        ax = show(
            basemaps,
            extent = [
                basemaps.bounds[0],
                basemaps.bounds[2],
                basemaps.bounds[1],
                basemaps.bounds[3]
                ],
            ax = ax
            )
        
        fields.plot(ax = ax, column = extent_info['plotting_attribute'], cmap = legends['cmaps'],
                    figsize = (args['mapsWidth'], args['mapsHeight'])
                    )
        
        try:
            plt.savefig(
                planting_ratemap_path,
                dpi = args['dpi'],
                transparent = args['transparent'],
                bbox_inches = args['bbox_inches'],
                pad_inches = args['pad_inches']
                )
        finally:
            shutil.rmtree(extent_info['temp_dir'])
            extent_info.pop('temp_dir')
            shutil.rmtree(os.path.dirname(extent_info['swath_filepath']))
            extent_info.pop('swath_filepath')
        return extent_info
