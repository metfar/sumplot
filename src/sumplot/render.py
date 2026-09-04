#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
import os;
from pathlib import Path;
from .spec import resolve;

def _matplotlib():
    try:
        import matplotlib.pyplot as plt;
    except ImportError as exc: raise RuntimeError("Plot rendering requires matplotlib: pip install matplotlib") from exc;
    return plt;

def figure(plot,width=8,height=6,dpi=100):
    plt=_matplotlib(); resolved=resolve(plot); fig,axis=plt.subplots(figsize=(float(width),float(height)),dpi=float(dpi));
    labels=dict(resolved.labels);
    for layer in resolved.layers:
        params=dict(layer.params); fill=params.get("fill",None); alpha=params.get("alpha",None);
        if layer.geom=="histogram":
            binwidth=float(layer.computed_value("width",1.0)); axis.bar(layer.x,layer.y,width=binwidth*0.95,color=fill,alpha=alpha,align="center");
        elif layer.geom=="bar":
            if layer.series:
                bottoms=[0.0]*len(layer.x);
                for name,values in layer.series:
                    axis.bar(range(len(values)),values,bottom=bottoms,label=name or None);
                    bottoms=[a+float(b) for a,b in zip(bottoms,values)];
                axis.set_xticks(range(len(layer.x)),[str(x) for x in layer.x]);
            else: axis.bar(range(len(layer.y)),layer.y,color=fill); axis.set_xticks(range(len(layer.x)),[str(x) for x in layer.x]);
        elif layer.geom=="bar3d":
            fig.delaxes(axis); axis=fig.add_subplot(111,projection="3d"); values=layer.y or tuple(sum(v for _,v in layer.series),()); axis.bar3d(range(len(values)),[0]*len(values),[0]*len(values),[0.8]*len(values),[0.8]*len(values),values,color=fill);
        elif layer.geom=="line": axis.plot(layer.x,layer.y,color=params.get("color",None));
        elif layer.geom=="scatter": axis.scatter(layer.x,layer.y,color=params.get("color",None));
    if labels.get("title"): axis.set_title(labels["title"]);
    if labels.get("x"): axis.set_xlabel(labels["x"]);
    if labels.get("y"): axis.set_ylabel(labels["y"]);
    fig.tight_layout(); return fig;

def ggsave(filename,plot,width=8,height=6,dpi=100,**kwargs):
    path=Path(filename); fig=figure(plot,width,height,dpi); fig.savefig(path,dpi=float(dpi),**kwargs); _matplotlib().close(fig); return str(path);

def show_plot(plot,block=False,width=8,height=6,dpi=100):
    plt=_matplotlib(); fig=figure(plot,width,height,dpi);
    backend=str(plt.get_backend()).lower(); display=bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or os.name=="nt");
    if display and "agg" not in backend: plt.show(block=bool(block));
    else: fig.canvas.draw();
    return fig;
