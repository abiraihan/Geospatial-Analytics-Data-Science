
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
import warnings
warnings.filterwarnings("ignore")

class Basemap:
    
    @classmethod
    def Extent(
            cls,
            filepaths:str,
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
            padding = 0,
            width_increase = None,
            height_increase = None
            )
        
        for key, value in size_args.items():
            if key in kwargs:
                size_args[key] = kwargs[key]
        
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
        
        if height.length > width.length:
            centroid_width = width.centroid
            xmax = centroid_width.x + (height.length)/2
            xmin = centroid_width.x - (height.length)/2
        elif height.length < width.length:
            centroid_height = height.centroid
            ymax = centroid_height.y + (width.length)/2
            ymin = centroid_height.y - (width.length)/2
        else:
            xmin, ymin, xmax, ymax = xmin, ymin, xmax, ymax
        
        width_length = shapely.geometry.LineString(
            (shapely.geometry.Point(xmax, ymax),
             shapely.geometry.Point(xmin, ymax))
            ).length
        height_length = shapely.geometry.LineString(
            (shapely.geometry.Point(xmin, ymax),
             shapely.geometry.Point(xmin, ymin))
            ).length
        
        if size_args['width_increase'] is not None:
            xmax = xmax + ((width_length/2)*size_args['width_increase'])/100
            xmin = xmin - ((width_length/2)*size_args['width_increase'])/100
        
        if size_args['height_increase'] is not None:
            ymax= ymax + ((height_length/2)*size_args['height_increase'])/100
            ymin = ymin - ((height_length/2)*size_args['height_increase'])/100
        
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
        assert oriented_poly.is_valid, 'Not a valid geometry, check def evaluate_polys at assert args'
        
        width_length_after = shapely.geometry.LineString(
            (shapely.geometry.Point(xmax, ymax),
             shapely.geometry.Point(xmin, ymax))
            ).length
        height_length_after = shapely.geometry.LineString(
            (shapely.geometry.Point(xmin, ymax),
             shapely.geometry.Point(xmin, ymin))
            ).length
        # print(width_length_after, height_length_after)
        if width_length_after > height_length_after:
            width_px = 1280
            height_px = int(1280/(width_length_after/height_length_after))
        elif width_length_after < height_length_after:
            width_px = int(1280*(width_length_after/height_length_after))
            height_px = 1280
        else:
            width_px = 1280
            height_px = 1280
        
        hyp_length = shapely.geometry.LineString((
            oriented_poly.centroid,
            shapely.geometry.Point(xmax, ymax))
            ).length
        increase_padding = lambda x, hyp_length : int((hyp_length + (hyp_length*(x/100))) - hyp_length)
        
        padding_length = increase_padding(size_args['padding'], hyp_length)
        
        buf = oriented_poly.buffer(
            padding_length,
            resolution = 4,
            cap_style = 3,
            join_style = 2,
            mitre_limit = 5,
            single_sided = True
            )
        
        trans_polys = shapely.ops.transform(
            projection(3857, target_crs),
            buf)
        
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
                'temp_tif': temp_tif,
                'temp_png': temp_png
                }
    
    @staticmethod
    def Boundary(extent_info, outpath, **kwargs):
        
        args = dict(
            image_border_width = 2,
            image_border_color = 'black',
            facecolor = 'grey',
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
                
        fields = gpd.read_file(extent_info['filepath'])
        
        basemaps = rasterio.open(extent_info['temp_tif'])
        
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
        
        extent_info['boundary_map_path'] = png_image_path
        
        return extent_info
    
    @staticmethod
    def Rxmap(extent_info, target_rate, outpath, **kwargs):
        
        args = dict(
            image_border_width = 2,
            image_border_color = 'black',
            facecolor = 'grey',
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
        sorted_target_val = sorted(fields[target_rate].unique().tolist())
        cmaps = Colorbar.Legend(sorted_target_val, colorbar_filepath = legend_path)
        basemaps = rasterio.open(extent_info['temp_tif'])
        
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
        fields.plot(
            ax=ax, column = target_rate, cmap = cmaps, legend = False,
            edgecolor = args['edgecolor'], linewidth = args['linewidth'],
            alpha = args['alpha']
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
        
        extent_info['basenames'] = {
                'legend': legend_path,
                'map': png_rxmap_path
                }
        return extent_info
