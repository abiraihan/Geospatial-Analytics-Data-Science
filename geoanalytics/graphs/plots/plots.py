# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager, colormaps

class Plots:
    
    @staticmethod
    def fonts():
        """
        Returns
        -------
        dict
            - fontpath values with font name as key
    
        """
        font_dirs ='../../reporting/fonts'
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
            font_name = 'Avenir LT Std 45 Book Oblique',
            plt_margin = 0.0,
            font_size = 12,
            font_style = 'oblique',
            width = 6,
            height = 0.3,
            alpha = 0.4,
            pad = 0,
            dpi = 300,
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
                prop = font_manager.FontProperties(fname = cls.fonts()[bar_args['font_name']])
                prop.set_size(bar_args['font_size'])
                prop.set_style(bar_args['font_style'])
            else:
                raise ValueError(f" -> '{bar_args['font_name']}' font is not available.\
                                 Available fonts are {list(cls.fonts().keys())}")
        
        xlocs = [i for i in range(0, len(list(cls.data.values())))]
        ax.bar([str(i) for i in list(cls.data.keys())], list(cls.data.values()), bottom = 0.0,
               color = bar_args['color'], alpha = bar_args['alpha'], width = 0.95)
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
            plt.text(
                xlocs[i] - 0.10,
                v + int(np.std(list(cls.data.values()))),
                str(v),
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

bar_args = dict(
    bar_filepath = None,
    font_name = 'Avenir LT Std 65 Medium',
    plt_margin = 0.0,
    font_size = 12,
    font_style = 'oblique',
    width = 2,
    height = 0.16,
    alpha = 1,
    pad = 4,
    dpi = 300,
    color = 'RdYlGn',
    transparent = True,
    bbox_inches = 'tight',
    pad_inches = 0.00
    )
data = {'DKC70-27': 15.56, 'P1222YHR': 5.6, 'POLAU': 55.3, 'P1222HR': 100.02, 'OBSESSION-II': 123.5, 
        'DKC70-27YHR': 50, 'DYNAGRO': 10.2}

fig, ax = plt.subplots(
    figsize = (bar_args['width']*len(data), bar_args['height'])
    )

plt.margins(bar_args['plt_margin'])

if bar_args['font_name'] is not None:
    if bar_args['font_name'] in list(Plots.fonts().keys()):
        prop = font_manager.FontProperties(fname = Plots.fonts()[bar_args['font_name']])
        prop.set_size(bar_args['font_size'])
        prop.set_style(bar_args['font_style'])
    else:
        raise ValueError(f" -> '{bar_args['font_name']}' font is not available.\
                         Available fonts are {list(Plots.fonts().keys())}")


colors = colormaps['tab20'].resampled(len(data))
xlocs = [i for i in range(0, len(list(data.values())))]
ax.bar([str(i) for i in list(data.keys())], 1, bottom = 2,
       color = colors(np.linspace(0, 1, len(data))), alpha = bar_args['alpha'], width = 0.9)
for border in ['top', 'right', 'left', 'bottom']:
    ax.spines[border].set_visible(False)
ax.tick_params(
    bottom = False,
    left = False, direction='in',
    pad = bar_args['pad']
    )
ax.set_yticks([])
ax.set_xticks([])
for i, v in enumerate(list(data.values())):
    plt.text(
        xlocs[i] - 0.05*len(str(v)),
        0.70,
        f"{str(v)} ac",
        font_properties = prop
        )

for i, v in enumerate(list(data.keys())):
    prop.set_size(12)
    if len(v) > 8:
        prop.set_size(10)
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
plt.show()
# =============================================================================
# ds = {0: 111.2, 1133: 325.2, 1360: 222.1}
# 
# Plots.Barcharts(ds, bar_filepath = '/home/kali/spark_out/bar.png')
# =============================================================================


