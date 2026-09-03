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
from dataclasses import dataclass, field;
import math;

@dataclass(frozen=True)
class Expr: pass;
@dataclass(frozen=True)
class ColumnRef(Expr): name: str;
@dataclass(frozen=True)
class Literal(Expr): value: object;
@dataclass(frozen=True)
class BinaryExpr(Expr): op: str; left: Expr; right: Expr;
@dataclass(frozen=True)
class CallExpr(Expr): name: str; args: tuple = field(default_factory=tuple);
@dataclass(frozen=True)
class AfterStat(Expr): name: str;
@dataclass(frozen=True)
class AesSpec:
    mappings: tuple = field(default_factory=tuple);
    def get(self,name,default=None): return dict(self.mappings).get(name,default);
    @classmethod
    def from_dict(cls,value): return cls(tuple((str(k), expr(v)) for k,v in dict(value or {}).items()));
@dataclass(frozen=True)
class LayerSpec:
    geom: str; aes: AesSpec = field(default_factory=AesSpec); stat: str = "identity"; position: str = "identity"; params: tuple = field(default_factory=tuple);
@dataclass(frozen=True)
class PlotSpec:
    data: object = None; aes: AesSpec = field(default_factory=AesSpec); layers: tuple = field(default_factory=tuple); labels: tuple = field(default_factory=tuple); theme: tuple = field(default_factory=tuple); options: tuple = field(default_factory=tuple);
    def add(self, layer): return PlotSpec(self.data,self.aes,self.layers+(layer,),self.labels,self.theme,self.options);
    def option(self,name,default=None): return dict(self.options).get(name,default);
@dataclass(frozen=True)
class ResolvedLayer:
    geom: str; x: tuple=(); y: tuple=(); groups: tuple=(); series: tuple=(); params: tuple=();
@dataclass(frozen=True)
class ResolvedPlot:
    layers: tuple; labels: tuple=(); options: tuple=();

def expr(value):
    if isinstance(value,Expr): return value;
    if isinstance(value,str): return ColumnRef(value);
    return Literal(value);

def _column(data,name):
    if hasattr(data,"columns") and isinstance(getattr(data,"columns"),dict): return list(data.columns[name]);
    if isinstance(data,dict): return list(data[name]);
    try: return list(data[name]);
    except Exception as exc: raise KeyError(name) from exc;

def evaluate(node,data,computed=None):
    computed=dict(computed or {});
    if isinstance(node,ColumnRef): return _column(data,node.name);
    if isinstance(node,Literal): return node.value;
    if isinstance(node,AfterStat): return computed[node.name];
    if isinstance(node,BinaryExpr):
        a=evaluate(node.left,data,computed); b=evaluate(node.right,data,computed);
        def apply(x,y): return {"+":lambda:x+y,"-":lambda:x-y,"*":lambda:x*y,"/":lambda:x/y,"**":lambda:x**y}[node.op]();
        if isinstance(a,(list,tuple)) or isinstance(b,(list,tuple)):
            aa=list(a) if isinstance(a,(list,tuple)) else [a]; bb=list(b) if isinstance(b,(list,tuple)) else [b]; n=max(len(aa),len(bb)); return [apply(aa[i%len(aa)],bb[i%len(bb)]) for i in range(n)];
        return apply(a,b);
    if isinstance(node,CallExpr):
        args=[evaluate(x,data,computed) for x in node.args]; name=node.name.lower();
        funcs={"log":math.log,"sqrt":math.sqrt,"factor":lambda x:x};
        if name not in funcs: raise ValueError("Unsupported expression function: {}".format(node.name));
        fn=funcs[name]; value=args[0]; return [fn(x) for x in value] if isinstance(value,(list,tuple)) else fn(value);
    return node;

def resolve(spec):
    layers=[];
    for layer in spec.layers:
        mappings=dict(spec.aes.mappings); mappings.update(dict(layer.aes.mappings));
        x=evaluate(mappings.get("x",Literal([])),spec.data); y=evaluate(mappings.get("y",Literal([])),spec.data);
        groups=evaluate(mappings.get("fill",mappings.get("color",Literal([]))),spec.data);
        if layer.geom in ("bar","bar3d") and layer.position=="stack" and groups:
            categories=[]; series={};
            for xv,yv,gv in zip(x,y,groups):
                if xv not in categories: categories.append(xv);
                series.setdefault(gv,{cat:0.0 for cat in categories});
                for values in series.values(): values.setdefault(xv,0.0);
                series[gv][xv]+=float(yv);
            packed=tuple((str(group),tuple(values.get(cat,0.0) for cat in categories)) for group,values in series.items());
            layers.append(ResolvedLayer(layer.geom,tuple(categories),(),tuple(groups),packed,layer.params));
        else: layers.append(ResolvedLayer(layer.geom,tuple(x) if isinstance(x,(list,tuple)) else (x,),tuple(y) if isinstance(y,(list,tuple)) else (y,),tuple(groups) if isinstance(groups,(list,tuple)) else (),(),layer.params));
    return ResolvedPlot(tuple(layers),spec.labels,spec.options);
