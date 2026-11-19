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

from .angle import rad2deg;
from .spec import resolve;


def _matplotlib():
    try:
        import matplotlib.pyplot as plt;
    except ImportError as exc:
        raise RuntimeError(
            "Plot rendering requires matplotlib: pip install matplotlib"
        ) from exc;
    return plt;


def _render_polar_bar(axis, layer, coord):
    if layer.series:
        names = [str(name) for name, _ in layer.series];
        values = [sum(float(value) for value in series) for _, series in layer.series];
    else:
        names = [str(value) for value in layer.x];
        values = [float(value) for value in layer.y];

    labels = names if any(names) else None;
    axis.pie(
        values,
        labels=labels,
        startangle=rad2deg(coord.start),
        counterclock=coord.direction > 0,
    );
    axis.axis("equal");


def figure(plot,width=8,height=6,dpi=100):
    plt=_matplotlib();
    resolved=resolve(plot);
    fig,axis=plt.subplots(figsize=(float(width),float(height)),dpi=float(dpi));
    labels=dict(resolved.labels);
    coord=resolved.coord;

    if coord.kind=="polar":
        polar_layers=[layer for layer in resolved.layers if layer.geom in ("bar","histogram")];
        if len(polar_layers)!=1 or len(resolved.layers)!=1:
            raise ValueError("coord_polar() currently supports one bar/histogram layer");
        _render_polar_bar(axis,polar_layers[0],coord);
    else:
        flipped=coord.kind=="flip";
        for layer in resolved.layers:
            params=dict(layer.params); fill=params.get("fill",None); alpha=params.get("alpha",None);
            if layer.geom=="histogram":
                binwidth=float(layer.computed_value("width",1.0));
                if flipped: axis.barh(layer.x,layer.y,height=binwidth*0.95,color=fill,alpha=alpha,align="center");
                else: axis.bar(layer.x,layer.y,width=binwidth*0.95,color=fill,alpha=alpha,align="center");
            elif layer.geom=="bar":
                if layer.series:
                    positions=range(len(layer.x));
                    totals=[0.0]*len(layer.x);
                    for name,values in layer.series:
                        if flipped: axis.barh(positions,values,left=totals,label=name or None);
                        else: axis.bar(positions,values,bottom=totals,label=name or None);
                        totals=[a+float(b) for a,b in zip(totals,values)];
                    if flipped: axis.set_yticks(list(positions),[str(x) for x in layer.x]);
                    else: axis.set_xticks(list(positions),[str(x) for x in layer.x]);
                else:
                    positions=range(len(layer.y));
                    if flipped:
                        axis.barh(positions,layer.y,color=fill,alpha=alpha);
                        axis.set_yticks(list(positions),[str(x) for x in layer.x]);
                    else:
                        axis.bar(positions,layer.y,color=fill,alpha=alpha);
                        axis.set_xticks(list(positions),[str(x) for x in layer.x]);
            elif layer.geom=="bar3d":
                fig.delaxes(axis); axis=fig.add_subplot(111,projection="3d"); values=layer.y or tuple(sum(v for _,v in layer.series),()); axis.bar3d(range(len(values)),[0]*len(values),[0]*len(values),[0.8]*len(values),[0.8]*len(values),values,color=fill);
            elif layer.geom=="line":
                if flipped: axis.plot(layer.y,layer.x,color=params.get("color",None),alpha=alpha);
                else: axis.plot(layer.x,layer.y,color=params.get("color",None),alpha=alpha);
            elif layer.geom=="scatter":
                if flipped: axis.scatter(layer.y,layer.x,color=params.get("color",None),alpha=alpha);
                else: axis.scatter(layer.x,layer.y,color=params.get("color",None),alpha=alpha);

    if labels.get("title"): axis.set_title(labels["title"]);
    if coord.kind=="flip":
        if labels.get("y"): axis.set_xlabel(labels["y"]);
        if labels.get("x"): axis.set_ylabel(labels["x"]);
    else:
        if labels.get("x"): axis.set_xlabel(labels["x"]);
        if labels.get("y"): axis.set_ylabel(labels["y"]);

    if coord.kind!="polar":
        if coord.xlim is not None:
            if coord.kind=="flip": axis.set_ylim(coord.xlim);
            else: axis.set_xlim(coord.xlim);
        if coord.ylim is not None:
            if coord.kind=="flip": axis.set_xlim(coord.ylim);
            else: axis.set_ylim(coord.ylim);

    fig.tight_layout();
    return fig;


def ggsave(filename,plot,width=8,height=6,dpi=100,**kwargs):
    path=Path(filename);
    fig=figure(plot,width,height,dpi);
    fig.savefig(path,dpi=float(dpi),**kwargs);
    _matplotlib().close(fig);
    return str(path);


def show_plot(plot,block=False,width=8,height=6,dpi=100):
    plt=_matplotlib();
    fig=figure(plot,width,height,dpi);
    backend=str(plt.get_backend()).lower();
    display=bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or os.name=="nt");
    if display and "agg" not in backend: plt.show(block=bool(block));
    else: fig.canvas.draw();
    return fig;
