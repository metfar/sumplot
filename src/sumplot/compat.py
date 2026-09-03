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
from .spec import AesSpec, AfterStat, ColumnRef, LayerSpec, PlotSpec;
def aes(**kwargs): return AesSpec.from_dict(kwargs);
def ggplot(data=None, mapping=None): return PlotSpec(data=data,aes=mapping or AesSpec());
def geom_point(mapping=None,**kwargs): return LayerSpec("scatter",mapping or AesSpec(),params=tuple(kwargs.items()));
def geom_line(mapping=None,**kwargs): return LayerSpec("line",mapping or AesSpec(),params=tuple(kwargs.items()));
def geom_bar(mapping=None,stat="identity",position="stack",**kwargs): return LayerSpec("bar",mapping or AesSpec(),stat=stat,position=position,params=tuple(kwargs.items()));
def geom_bar3d(mapping=None,stat="identity",position="stack",**kwargs): return LayerSpec("bar3d",mapping or AesSpec(),stat=stat,position=position,params=tuple(kwargs.items()));
def after_stat(name): return AfterStat(str(name));
