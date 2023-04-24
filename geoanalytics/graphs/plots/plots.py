
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager, colormaps
from matplotlib.colors import ListedColormap

class Plots:
    
    @staticmethod
    def fonts():
        """
        Returns
        -------
        dict
            - fontpath values with font name as key
    
        """
        font_dirs ='/home/kali/geolytics/Geospatial-Analytics-Data-Science/geoanalytics/reporting/fonts/'
        return {
            os.path.basename(i).split('.', 1)[0]:i
            for i in [
                    os.path.join(
                        font_dirs, i
                        )
                    for i in os.listdir(font_dirs)
                    if os.path.basename(i).split('.', 1)[1] == 'ttf'
                    ]
                 }
    @classmethod
    def Barcharts(
            cls,
            data:dict,
            **kwargs
            ):
        """

        Parameters
        ----------
        data : dict
            DESCRIPTION. Key pair values for key as lebel and values as counts
        **kwargs : TYPE
            DESCRIPTION. Keywords args for bar plot customization.

        Raises
        ------
        ValueError
            DESCRIPTION. Raise ValueError if keywords arg for 'bar_filepath' \
                is not provided for a valid path to export plot images

        Returns
        -------
        TYPE
            DESCRIPTION. Plot image path location as provided for keyword args \
                for 'bar_filepath'.

        """
        
        cls.data = data
        
        bar_args = dict(
            bar_filepath = None,
            font_name = 'Avenir LT Std 55 Book Oblique',
            plt_margin = 0.0,
            font_size = 12,
            font_style = 'oblique',
            width = 6,
            height = 0.3,
            alpha = 0.4,
            pad = 0,
            dpi = 300,
            label_xaxis = 0.25,
            label_yaxis = 5,
            label_box_width = 0.95,
            color = 'grey',
            transparent = True,
            bbox_inches = 'tight',
            pad_inches = 0.00
            )
        
        for key, value in bar_args.items():
            if key in kwargs:
                bar_args[key] = kwargs[key]
        if bar_args['bar_filepath'] is None:
            raise ValueError("Bar Path Location can not be left empty or assign None ! ")
        
        fig, ax = plt.subplots(
            figsize = (bar_args['width'], bar_args['height'])
            )
        
        plt.margins(bar_args['plt_margin'])
        
        if bar_args['font_name'] is not None:
            if bar_args['font_name'] in list(cls.fonts().keys()):
                prop = font_manager.FontProperties(
                    fname = cls.fonts()[bar_args['font_name']]
                    )
                prop.set_size(bar_args['font_size'])
                prop.set_style(bar_args['font_style'])
            else:
                raise ValueError(f" -> '{bar_args['font_name']}' font is not available.\
                                 Available fonts are {list(cls.fonts().keys())}")
        
        xlocs = [i for i in range(0, len(list(cls.data.values())))]
        ax.bar([str(i) for i in list(cls.data.keys())], list(cls.data.values()), bottom = 0.0,
               color = bar_args['color'], alpha = bar_args['alpha'], width = bar_args['label_box_width'])
        for border in ['top', 'right', 'left', 'bottom']:
            ax.spines[border].set_visible(False)
        ax.tick_params(
            bottom = False,
            left = False, direction='in',
            pad = bar_args['pad']
            )
        ax.set_yticks([])
        ax.set_xticks([])
        for i, v in enumerate(list(cls.data.values())):
            if v != 0:
                plt.text(
                    xlocs[i] - bar_args['label_xaxis'],
                    v + bar_args['label_yaxis'],
                    str(v),
                    font_properties = prop
                    )
            else:
                plt.text(
                    xlocs[i] - bar_args['label_xaxis'],
                    v + bar_args['label_yaxis'],
                    "",
                    font_properties = prop
                    )
        plt.savefig(
            bar_args['bar_filepath'],
            dpi = bar_args['dpi'],
            transparent = bar_args['transparent'],
            bbox_inches = bar_args['bbox_inches'],
            pad_inches = bar_args['pad_inches']
            )
        return bar_args['bar_filepath']
    
    @staticmethod
    def PlantingLegendBar(graph_data:dict, **kwargs)-> dict:
        
        legend_args = dict(
            png_filepath = None,
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
            dpi = 300,
            color = 'tab20',
            transparent = True,
            bbox_inches = 'tight',
            pad_inches = 0.00,
            auto_font_dicts = {'start': 9, 'stop': 30, 'interval': 5}
            )
        for key, value in legend_args.items():
            if key in kwargs:
                legend_args[key] = kwargs[key]
                
        if legend_args['png_filepath'] is None:
            raise ValueError("PNG image Path 'png_filepath' keywords can not be left empty or unassigned! ")
        
        lengths = max([len(i) for i, _ in graph_data.items()])
        
        if lengths > 10:
            legend_args['width'] = 2
        else:
            legend_args['width'] = 1.5
        
        if any([len(i) > 16 for i, j in graph_data.items()]):
            legend_args['width'] = 2.3
        
        import matplotlib
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        fig, ax = plt.subplots(
            figsize = (
                legend_args['width']*len(graph_data),
                legend_args['height']
                )
            )
        
        plt.margins(legend_args['plt_margin'])

        if legend_args['font_name'] is not None:
            if legend_args['font_name'] in list(Plots.fonts().keys()):
                prop = font_manager.FontProperties(
                    fname = Plots.fonts()[legend_args['font_name']]
                    )
                prop.set_size(legend_args['font_size'])
                prop.set_style(legend_args['font_style'])
            else:
                raise ValueError(f" -> '{legend_args['font_name']}' font is not available.\
                                  Available fonts are {list(Plots.fonts().keys())}")
        
        colors = colormaps[legend_args['color']].resampled(len(graph_data))
        
        color_dicts = dict(zip(
            list(graph_data.keys()),
            list(colors(np.linspace(0, 1, len(graph_data))).tolist())
            ))
        
        color_val = {i:tuple(j) for i, j in color_dicts.items()}
        
        xlocs = [i for i in range(0, len(list(graph_data.values())))]
        ax.bar([str(i) for i in list(graph_data.keys())], 1, bottom = 2,
                color = colors(np.linspace(0, 1, len(graph_data))),
                alpha = legend_args['alpha'], width = 0.9)
        
        for border in ['top', 'right', 'left', 'bottom']:
            ax.spines[border].set_visible(False)
        ax.tick_params(
            bottom = False,
            left = False, direction='in',
            pad = legend_args['pad']
            )
        ax.set_yticks([])
        ax.set_xticks([])
        for i, v in enumerate(list(graph_data.values())):
            plt.text(
                xlocs[i] - 0.05*len(str(v)),
                0.70,
                f"{str(v)} ac",
                font_properties = prop
                )
        #TODO - set def for 'auto_font_dict; follow def 'PlantingRateBarLegend' into set_xspace and set y_space def 
        if legend_args['auto_font_dicts'] is not None:
            font_length_interval = {int(i): 24 - ((int(i)//legend_args['auto_font_dicts']['interval']) + 13)
                   for i in np.linspace(
                           legend_args['auto_font_dicts']['start'],
                           legend_args['auto_font_dicts']['stop'],
                           int(legend_args['auto_font_dicts']['stop']
                               - legend_args['auto_font_dicts']['start'])
                           )
                   }
                
            for i, v in enumerate(list(graph_data.keys())):
                prop.set_size(12)
                if any([len(v) > i for i in list(font_length_interval.keys())]):
                    prop.set_size(font_length_interval[len(v)])
                    set_posx = len(v)*0.03
                else:
                    set_posx = len(v)*0.04
                # set_posx = len(v)*0.04
                plt.text(
                    xlocs[i] - set_posx,
                    3.4,
                    str(v),
                    font_properties = prop
                    )
        else:
            for i, v in enumerate(list(graph_data.keys())):
                prop.set_size(12)
                if len(v) > legend_args['font_length_limit']:
                    prop.set_size(legend_args['variety_font_size'])
                    set_posx = len(v)*0.03
                else:
                    set_posx = len(v)*0.04
                # set_posx = len(v)*0.04
                plt.text(
                    xlocs[i] - set_posx,
                    3.4,
                    str(v),
                    font_properties = prop
                    )
        plt.savefig(
            legend_args['png_filepath'],
            dpi = legend_args['dpi'],
            transparent = legend_args['transparent'],
            bbox_inches = legend_args['bbox_inches'],
            pad_inches = legend_args['pad_inches']
            )
        return {
            'png_filepath': legend_args['png_filepath'],
            'cmaps': colors,
            'cmaps_vals': color_val,
            'type': 'Bar'
            }
            
    @staticmethod
    def PlantingScatterLegend(graph_data:dict, **kwargs)-> dict:
        
        legend_args = dict(
            png_filepath = None,
            plt_margin = 0.0,
            font_name = 'Avenir LT Std 65 Medium Oblique',
            font_size = 12,
            font_style = 'oblique',
            frameon = False,
            markerscale = 1.5,
            markerfirst =  True,
            alignment = 'left',
            labelspacing = 0.4,
            framealpha = 1,
            handlelength = 0.3,
            handleheight = 0.0,
            borderaxespad = 0.1,
            dpi = 300,
            color = 'tab20',
            transparent = True,
            bbox_inches = 'tight',
            pad_inches = 0.00
            )
        for key, value in legend_args.items():
            if key in kwargs:
                legend_args[key] = kwargs[key]
        
        if legend_args['png_filepath'] is None:
            raise ValueError("PNG image Path 'png_filepath' keywords can not be left empty or unassigned! ")
        
        colors = colormaps[legend_args['color']].resampled(len(graph_data))
        color_dicts = dict(zip(
            list(graph_data.keys()),
            list(colors(np.linspace(0, 1, len(graph_data))).tolist())
            ))
        color_val = {i:tuple(j) for i, j in color_dicts.items()}
        
        import matplotlib
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        fig, ax = plt.subplots(
            figsize = (
                2.9,
                len(graph_data)* 0.3125
                )
            )
        plt.margins(legend_args['plt_margin'])
        if legend_args['font_name'] is not None:
            if legend_args['font_name'] in list(Plots.fonts().keys()):
                prop = font_manager.FontProperties(
                    fname = Plots.fonts()[legend_args['font_name']]
                    )
                prop.set_size(legend_args['font_size'])
                prop.set_style(legend_args['font_style'])
            else:
                raise ValueError(f" -> '{legend_args['font_name']}' font is not available.\
                                  Available fonts are {list(Plots.fonts().keys())}")
        
        legend_func = lambda m, c: plt.plot([], [], marker = m, color = c, linestyle='None')[0]
        variety_marker = [legend_func("o", j) for i, j in color_val.items()]
        variety_name = [i for i, j in color_val.items()]
        
        legend_kws = ['frameon','markerscale', 'markerfirst', 'alignment', 'labelspacing',
        'framealpha', 'handlelength', 'handleheight', 'borderaxespad']
        
        anchor_space = max([len(i)/20 for i , j in graph_data.items()]) + 0.13
        
        variety_legend = ax.legend(
            variety_marker, variety_name,
            bbox_to_anchor = (anchor_space, 1),
            prop = prop,
            **{i:kwargs[i] for i in legend_kws}
            )
        
        ax.add_artist(variety_legend)
        
        area_marker = [legend_func("", j) for i, j in color_val.items()]
        area_values = [f"{graph_data[i]} ac" for i, j in color_val.items()]
        
        ax.legend(
            area_marker, area_values,
            bbox_to_anchor = (anchor_space + 0.41, 1),
            prop = prop,
            **{i:kwargs[i] for i in legend_kws}
            )
        
        for border in ['top', 'right', 'left', 'bottom']:
            ax.spines[border].set_visible(False)
        ax.tick_params(
            bottom = False,
            left = False, direction='in',
            pad = 0
            )
        ax.set_yticks([])
        ax.set_xticks([])
        ax.xaxis.set_major_locator(matplotlib.ticker.NullLocator())
        ax.yaxis.set_major_locator(matplotlib.ticker.NullLocator())
        plt.savefig(
            legend_args['png_filepath'],
            dpi = legend_args['dpi'],
            transparent = legend_args['transparent'],
            bbox_inches = legend_args['bbox_inches'],
            pad_inches = legend_args['pad_inches']
            )
        return {
            'png_filepath': legend_args['png_filepath'],
            'cmaps': colors,
            'cmaps_vals': color_val,
            'type': 'Scatter'
            }
    
    @classmethod
    def PlantingVarietyLegend(cls, graphs_data, **kwargs):
        
        cls.graphs_data = graphs_data
                
        if len(graphs_data) < kwargs['num_variety']:
            planting_legend = cls.PlantingLegendBar(
                cls.graphs_data,
                **kwargs
                )
        else:
            planting_legend = cls.PlantingScatterLegend(
                cls.graphs_data,
                **kwargs
                )
        return planting_legend
    
    @staticmethod
    def PlantingRateBarLegend(datas:dict, **kwargs):
    
        legend_args = dict(
            bar_legend_filepath = None,
            font_name = 'Avenir LT Std 55 Oblique',
            plt_margin = 0.0,
            font_size = 14,
            font_style = 'oblique',
            width = 12,
            bar_height = 0.6,
            alpha = 0.9,
            pad = 0,
            dpi = 300,
            bar_label_box_width = 0.97,
            bar_color = 'lightgrey',
            transparent = True,
            bbox_inches = 'tight',
            pad_inches = 0.00
            )
        
        for key, value in legend_args.items():
            if key in kwargs:
                legend_args[key] = kwargs[key]
        
        import matplotlib
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
                
        if legend_args['bar_legend_filepath'] is None:
            raise ValueError("PNG image Path 'bar_legend_filepath' keywords can not be left empty or unassigned! ")
        
        insert_symbol = list(datas.items())
        insert_symbol.insert(0, ('<', 0))
        
        data = dict(insert_symbol)
        
        fig, ax = plt.subplots(
            figsize = (legend_args['width'], legend_args['bar_height'])
            )
        
        plt.margins(legend_args['plt_margin'])
        plt.rcParams["figure.figsize"] = (legend_args['width'], legend_args['bar_height'])
        plt.rcParams['xtick.major.pad'] = 0
        plt.rcParams['xtick.alignment'] = 'center'
        if legend_args['font_name'] is not None:
            if legend_args['font_name'] in list(Plots.fonts().keys()):
                prop = font_manager.FontProperties(
                    fname = Plots.fonts()[legend_args['font_name']]
                    )
                prop.set_size(legend_args['font_size'])
                prop.set_style(legend_args['font_style'])
            else:
                raise ValueError(f" -> '{legend_args['font_name']}' font is not available.\
                                  Available fonts are {list(Plots.fonts().keys())}")
                                  
        def set_xspace(val):
            if len(str(val)) > 5:
                prop.set_size(10)
                space = 0.5
            elif len(str(val)) == 5:
                space = 0.58
            elif len(str(val)) == 4:
                space = 0.45
            elif len(str(val)) == 3:
                space = 0.3
            else:
                space  = 0.15
            return space
        
        xlocs = [i for i in range(0, len(list(data.values())))]
        ax.bar([str(i) for i in list(data.keys())], list(data.values()), bottom = 0,
                color = legend_args['bar_color'], alpha = legend_args['alpha'], width = legend_args['bar_label_box_width'])
        for border in ['top', 'right', 'left', 'bottom']:
            ax.spines[border].set_visible(False)
        
        ax.tick_params(
            bottom = False,
            left = False, direction='in',
            pad = legend_args['pad']
            )
        ax.set_yticks([])
        ax.set_xticks([])
        
        def set_yspace(val_dict):
            df = max([i for i in list(val_dict.values())])
            if df > 1000:
                space = 81
            elif 100 < df < 1000:
                space = 9
            elif 10 < df < 100:
                space = 2
            elif 4 < df < 10:
                space = 0.8
            else:
                space = 0.2
            return space
        
        for i, v in enumerate(list(data.values())):
            prop.set_size(legend_args['font_size'])
            if v != 0:
                plt.text(
                    xlocs[i] - set_xspace(v),
                    v + set_yspace(data),
                    str(v),
                    font_properties = prop
                    )
            else:
                plt.text(
                    xlocs[i] - set_xspace(v),
                    v + np.std([j for i, j in data.items()]),
                    "",
                    font_properties = prop
                    )
        plt.savefig(
            legend_args['bar_legend_filepath'],
            dpi = legend_args['dpi'],
            transparent = legend_args['transparent'],
            bbox_inches = legend_args['bbox_inches'],
            pad_inches = legend_args['pad_inches']
            )
        return {
            'bar_legend_filepath': legend_args['bar_legend_filepath']
            }
    
    
    @staticmethod
    def PlantingRateColorLegend(datas:dict, **kwargs):
    
        legend_args = dict(
            cmaps_legend_filepath = None,
            font_name = 'Avenir LT Std 55 Oblique',
            plt_margin = 0.0,
            font_size = 14,
            font_style = 'oblique',
            width = 12,
            cmaps_height = 0.2,
            alpha = 0.9,
            pad = 0,
            dpi = 300,
            cmaps_label_box_width = 1.0,
            cmaps_color = 'RdYlGn',
            transparent = True,
            bbox_inches = 'tight',
            pad_inches = 0.00
            )
        
        for key, value in legend_args.items():
            if key in kwargs:
                legend_args[key] = kwargs[key]
                
        import matplotlib
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        
        if legend_args['cmaps_legend_filepath'] is None:
            raise ValueError("PNG image Path 'cmaps_legend_filepath' keywords can not be left empty or unassigned! ")
        
        if legend_args['font_name'] is not None:
            if legend_args['font_name'] in list(Plots.fonts().keys()):
                prop = font_manager.FontProperties(
                    fname = Plots.fonts()[legend_args['font_name']]
                    )
                prop.set_size(legend_args['font_size'])
                prop.set_style(legend_args['font_style'])
            else:
                raise ValueError(f" -> '{legend_args['font_name']}' font is not available.\
                                  Available fonts are {list(Plots.fonts().keys())}")
            
        cmaps = colormaps[legend_args['cmaps_color']].resampled(len(datas) + 2)
            
        insert_symbol = list(datas.items())
        insert_symbol.insert(len(insert_symbol), ('>', 0))
        
        data = dict(insert_symbol)
    
        fig, ax = plt.subplots(
            figsize = (
                legend_args['width'],
                legend_args['cmaps_height']
                )
            )
        plt.rcParams["figure.figsize"] = (legend_args['width'], legend_args['cmaps_height'])
        plt.margins(legend_args['plt_margin'])
        plt.rcParams['xtick.major.pad'] = 0
        plt.rcParams['xtick.alignment'] = 'center'
        
        ax.bar([str(i) for i in list(data.keys())],
               legend_args['cmaps_height'], bottom = 9,
                color = cmaps(np.linspace(0, 1, len(data))),
                alpha = legend_args['alpha'],
                width = legend_args['cmaps_label_box_width']
                )
        for border in ['top', 'right', 'left', 'bottom']:
            ax.spines[border].set_visible(False)
        ax.tick_params(
            bottom = False,
            left = False, direction='in',
            pad = 5
            )
        
        ax.set_yticks([])
        ax.set_xticks(
            [-0.36]
            + [i + 0.5
               if i != max([i for i in ax.get_xticks()])
               else i + 0.36 for i in ax.get_xticks()],
            ['<']+ [i for i in list(data.keys())]
            )
        
        for label in ax.get_xticklabels():
            label.set_fontproperties(prop)
            
        map_cmap = ListedColormap(cmaps(np.linspace(0, 1, len(data)))[1:])
        color_dict = dict(zip(list(datas.keys()), cmaps(np.linspace(0, 1, len(data)))[1:]))
        color_map = {i: tuple(j) for i, j in color_dict.items()}
    
        plt.savefig(
            legend_args['cmaps_legend_filepath'],
            dpi = legend_args['dpi'],
            transparent = legend_args['transparent'],
            bbox_inches = legend_args['bbox_inches'],
            pad_inches = legend_args['pad_inches']
            )
        return {
            'cmaps_legend_filepath': legend_args['cmaps_legend_filepath'],
            'cmaps': map_cmap,
            'cmaps_vals': color_map
            }
    
    @classmethod
    def PlantingRateLegend(cls, rates, **kwargs):
        
        cls.rates = rates
                
        import matplotlib
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        
        bar_legends = Plots.PlantingRateBarLegend(cls.rates, **kwargs)

        color_legends = Plots.PlantingRateColorLegend(
            cls.rates,
            **kwargs
            )
        bar_legends.update(color_legends)
        return bar_legends


# =============================================================================
# data = {30: 0.9, 31: 4, 32: 6.8, 33: 16.5, 34: 23.7, 35: 0.2, 36: 0.1, 37: 0.6, 38: 1}
# ds = Plots.PlantingRateBarLegend(data, bar_legend_filepath = './bar_def.png')
# fs = Plots.PlantingRateLegend(data, cmaps_legend_filepath = './barLeg_def.png')
# =============================================================================



# =============================================================================
# data = {'DKC70-27': 14.9,
#   'DKC62-70': 0.8,
#   'DKC69-99': 0.8,
#   'P1289YHR': 0.8,
#   'P17052YHR': 0.8,
#   'P124': 0.9}
# 
# data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
# legend_args = dict(
#     num_variety = 9,
#     png_filepath = 'planting_legend.png',
#     font_name = 'Avenir LT Std 65 Medium Oblique',
#     plt_margin = 0.0,
#     font_size = 12,
#     font_style = 'oblique',
#     width = 2,
#     height = 0.16,
#     alpha = 1,
#     pad = 4,
#     font_length_limit = 11,
#     variety_font_size = 10,
#     auto_font_dicts = {'start': 9, 'stop': 30, 'interval': 5},
#     dpi = 300,
#     color = 'tab20',
#     transparent = True,
#     bbox_inches = 'tight',
#     pad_inches = 0.00,
#     frameon = False,
#     markerscale = 1.5,
#     markerfirst =  True,
#     alignment = 'left',
#     labelspacing = 0.4,
#     framealpha = 1,
#     handlelength = 0.3,
#     handleheight = 0.0,
#     borderaxespad = 0.2
#     )
# vals = Plots.PlantingVarietyLegend(
#     data, **legend_args
#     )
# =============================================================================



# =============================================================================
# import geopandas as gpd
# 
# plant_data = '/home/kali/Data/Corn_AsPlanted'
# plantfiles = [os.path.join(plant_data, i) for i in os.listdir(plant_data) if os.path.basename(i).split('.', 1)[1] == 'shp'][2]
# 
# data = Report.Planting(plantfiles, *['Grower___N', 'Farm___Nam', 'Field___Na', 'Product___'])
# 
# data = gpd.read_file(plantfiles)
# =============================================================================


# =============================================================================
# plant_data = '/home/kali/Data/Corn_AsPlanted'
# rxfiles = [os.path.join(plant_data, i) for i in os.listdir(plant_data) if os.path.basename(i).split('.', 1)[1] == 'shp'][0]
# import geopandas as gpd
# 
# df = gpd.read_file(rxfiles)
# 
# ds = {0: 111.2, 1133: 325.2, 1360: 222.1}
# 
# Plots.Barcharts(ds, bar_filepath = '/home/kali/spark_out/bar.png')
# =============================================================================



