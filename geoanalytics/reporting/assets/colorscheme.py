
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

class Colorbar:
    
    @staticmethod
    def fonts():
        """
        Returns
        -------
        dict
            - fontpath values with font name as key

        """
        font_dirs = "../../reporting/fonts"
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
    
    @staticmethod
    def getCmap(values_list:list, cmap_name:str):
        """

        Parameters
        ----------
        values_list : list
            DESCRIPTION. Values that color map depends on to create a new cmap
        cmap_name : str
            DESCRIPTION. Available cmap from plt.colormap()

        Raises
        ------
        ValueError
            DESCRIPTION. If cmap_name is not a valid one.
        TypeError
            DESCRIPTION. If No color map generated under given args

        Returns
        -------
        cmaps : matplotlib.colors.LinearSegmentedColormap
            DESCRIPTION. cmap colormap that covers the values_list min and max

        """
        
        if cmap_name not in plt.colormaps():
            raise ValueError(f"{cmap_name} is not a valid cmap in colormap in matplotlib")
        
        sorted_list = sorted(values_list)
        if len(sorted_list) > 2:
            color_maps = mpl.colormaps[cmap_name].resampled(256)
        elif len(sorted_list) == 2:
            color_maps = mpl.colormaps[cmap_name].resampled(256)
        else:
            color_maps = mpl.colormaps[cmap_name].reversed().resampled(256)
        
        if 0 in sorted_list and len(sorted_list) > 1:
            min_vals = lambda x, perc : int(min([int(i) for i in x if i != 0]) - ((min([int(i) for i in x if i != 0])*perc)/100))
            int_val = min_vals(sorted_list, 15)
            # print(int_val)
            newcolors = color_maps(np.linspace(0, 1, int(max(sorted_list))+1 - int_val))
            grey = np.array([161/256, 161/256, 161/256, 1])
            new_cl = np.concatenate([[grey]*int_val,newcolors])
            list_int = [int(i) for i in sorted_list]
            color_index = ListedColormap(new_cl[list_int])
            color_ratio = [i/max(sorted_list) for i in sorted_list]
            cmaps = LinearSegmentedColormap.from_list(
                "my_cmap",
                list(zip(
                    color_ratio,
                    color_index(range(len(list_int))).tolist())
                    )
                )
        elif 0 not in sorted_list and len(sorted_list) > 1:
            newcolors = color_maps(
                np.linspace(0, 1, int(max(sorted_list)) + 1 - int(min(sorted_list)))
                )
            
            color_norms = lambda x_list : [(i-min(x_list))/(max(x_list)-min(x_list)) for i in x_list]
            color_ratio = color_norms(sorted_list)
            index_val = lambda x_list : [int(i-min(x_list)) for i in x_list]
            index = index_val(sorted_list)
            color_index = ListedColormap(newcolors[index])
            cmaps = LinearSegmentedColormap.from_list(
                "my_cmap",
                list(zip(
                    color_ratio,
                    color_index(range(len(sorted_list))).tolist())
                    )
                )
        elif 0 in sorted_list and len(sorted_list) == 1:
            grey = np.array([[161/256, 161/256, 161/256, 1],
                             [256/256, 256/256, 256/256, 1],
                             [0/256, 0/256, 0/256, 1]])
            color_index = ListedColormap(grey)
            newsc = color_index(np.linspace(0, 1, 256))
            cmaps = ListedColormap(newsc)
        elif 0 not in sorted_list and len(sorted_list) == 1:
            cmaps = mpl.colormaps[cmap_name].reversed().resampled(int(max(sorted_list)))
        else:
            raise TypeError("No valid colormap (cmap) generated!")
        return cmaps
    
    @classmethod
    def Legend(cls,
            data_list:list,
            **kwargs
            ):
        """

        Parameters
        ----------
        data_list : list
            DESCRIPTION. a list of values that color map depends on to create a new legend
        **kwargs : keyword args
            DESCRIPTION. keyword args for create legends & cmaps for geospatial maps

        Raises
        ------
        ValueError
            DESCRIPTION. To save png file, If data path location is not provided. 

        Returns
        -------
        cmaps : TYPE
            DESCRIPTION. cmap colormap that covers the values_list min and max

        """
        
        cls.data_list = data_list
        
        colorbar_args = dict(
            plt_margin = 0.0,
            colorbar_filepath = None,
            colormap = 'RdYlGn',
            font_name = 'Avenir LT Std 35 Light',
            font_size = 12,
            font_style = 'normal',
            width = 6,
            height = 0.3,
            alpha = 0.9,
            pad = 3,
            dpi = 300,
            transparent = True,
            bbox_inches = 'tight',
            pad_inches = 0.00,
            colorbar_num = 9
            )
        
        for key, value in colorbar_args.items():
            if key in kwargs:
                colorbar_args[key] = kwargs[key]
        
        if colorbar_args['colorbar_filepath'] is None:
            raise ValueError("Colorbar Path Location can not be empty! ")
        
        cmaps = cls.getCmap(
            values_list = cls.data_list,
            cmap_name = colorbar_args['colormap']
            )
        
        if colorbar_args['font_name'] is not None:
            if colorbar_args['font_name'] in list(cls.fonts().keys()):
                prop = fm.FontProperties(fname = cls.fonts()[colorbar_args['font_name']])
                prop.set_size(colorbar_args['font_size'])
                prop.set_style(colorbar_args['font_style'])
            else:
                raise ValueError(f" -> '{colorbar_args['font_name']}' font is not available.\
                                 Available fonts are {list(cls.fonts().keys())}")
            
        data = [int(i) for i in sorted(cls.data_list)]
        min_val, max_val = min(data), max(data)
        
        if len(data) < colorbar_args['colorbar_num']:
            fig, ax = plt.subplots(
                figsize = (colorbar_args['width'], colorbar_args['height'])
                )
            plt.margins(colorbar_args['plt_margin'])
            ax.imshow([data], cmap = cmaps, aspect = 'auto',
                      interpolation='nearest',
                      alpha = colorbar_args['alpha'])
            ax.set_xticks(np.arange(0, len(data), 1))
            ax.set_xticklabels(data)
            ax.set_yticks([])
            ax.tick_params(
                bottom = False,
                left = False, direction='in',
                pad = colorbar_args['pad']
                )
            for border in ['top', 'right', 'left', 'bottom']:
                ax.spines[border].set_visible(False)
            if colorbar_args['font_name'] is not None:
                for label in ax.get_xticklabels():
                    label.set_fontproperties(prop)
        else:
            fig, ax = plt.subplots(
                figsize = (colorbar_args['width'], colorbar_args['height'])
                )
            plt.margins(colorbar_args['plt_margin'])
            ax.imshow([data], cmap = cmaps, aspect = 'auto',
                      interpolation='nearest', alpha = colorbar_args['alpha']
                      )
            ax.set_yticks([0])
            ax.set_yticklabels([min_val])
            ax.set_xticks([])
            ax1 = ax.secondary_yaxis("right")
            ax1.set_yticks([0])
            ax1.set_yticklabels([max_val])
            ax.tick_params(
                bottom = False, left = False,
                direction='in',
                pad = colorbar_args['pad'])
            ax1.tick_params(
                bottom = False, right = False,
                direction='in',
                pad = colorbar_args['pad']
                )
            for border in ['top', 'right', 'left', 'bottom']:
                ax.spines[border].set_visible(False)
                ax1.spines[border].set_visible(False)
            if colorbar_args['font_name'] is not None:
                for label in ax.get_yticklabels():
                    label.set_fontproperties(prop)
                for label in ax1.get_yticklabels():
                    label.set_fontproperties(prop)
        plt.savefig(
            colorbar_args['colorbar_filepath'],
            dpi = colorbar_args['dpi'],
            transparent = colorbar_args['transparent'],
            bbox_inches = colorbar_args['bbox_inches'],
            pad_inches = colorbar_args['pad_inches']
            )
        return cmaps
