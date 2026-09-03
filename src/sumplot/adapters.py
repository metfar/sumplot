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
from sumui import ChartSeries, ChartSpec;
from .spec import resolve;

def to_chart_spec(plot):
    resolved=resolve(plot); layer=resolved.layers[0] if resolved.layers else None; labels=dict(resolved.labels);
    if layer is None: return ChartSpec("bar", title=labels.get("title",""));
    if layer.series:
        return ChartSpec("bar3d" if layer.geom=="bar3d" else "bar", title=labels.get("title",""), categories=layer.x, series=tuple(ChartSeries(name=name,values=values) for name,values in layer.series), stacked=True);
    if layer.geom in ("bar","bar3d"):
        return ChartSpec("bar3d" if layer.geom=="bar3d" else "bar", title=labels.get("title",""), categories=tuple(str(x) for x in layer.x), series=(ChartSeries(values=layer.y),));
    if layer.geom in ("line","scatter"):
        return ChartSpec(layer.geom,title=labels.get("title",""),series=(ChartSeries(x_values=layer.x,values=layer.y),));
    raise ValueError("No ChartSpec adapter for {}".format(layer.geom));
