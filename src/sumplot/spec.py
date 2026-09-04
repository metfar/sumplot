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
    def param(self,name,default=None): return dict(self.params).get(name,default);
@dataclass(frozen=True)
class PlotSpec:
    data: object = None; aes: AesSpec = field(default_factory=AesSpec); layers: tuple = field(default_factory=tuple); labels: tuple = field(default_factory=tuple); theme: tuple = field(default_factory=tuple); options: tuple = field(default_factory=tuple);
    def add(self,layer): return PlotSpec(self.data,self.aes,self.layers+(layer,),self.labels,self.theme,self.options);
    def __add__(self,layer): return self.add(layer);
    def option(self,name,default=None): return dict(self.options).get(name,default);
    def with_option(self,name,value):
        options=dict(self.options); options[str(name)]=value; return PlotSpec(self.data,self.aes,self.layers,self.labels,self.theme,tuple(options.items()));
@dataclass(frozen=True)
class ResolvedLayer:
    geom: str; x: tuple=(); y: tuple=(); groups: tuple=(); series: tuple=(); params: tuple=(); computed: tuple=();
    def param(self,name,default=None): return dict(self.params).get(name,default);
    def computed_value(self,name,default=None): return dict(self.computed).get(name,default);
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

def _finite_numbers(values):
    output=[];
    for value in values:
        try: number=float(value);
        except (TypeError,ValueError): continue;
        if math.isfinite(number): output.append(number);
    return output;

def _bin(values,binwidth=None,bins=None,boundary=None):
    numbers=_finite_numbers(values);
    if not numbers: return {"x":(),"count":(),"density":(),"width":1.0,"xmin":(),"xmax":()};
    minimum=min(numbers); maximum=max(numbers);
    if binwidth is None:
        bins=max(1,int(bins or 30)); span=maximum-minimum; binwidth=span/bins if span>0 else 1.0;
    width=float(binwidth);
    if width<=0: raise ValueError("binwidth must be greater than zero");
    origin=float(boundary) if boundary is not None else math.floor(minimum/width)*width;
    if origin>minimum: origin-=width;
    count=max(1,int(math.floor((maximum-origin)/width))+1);
    counts=[0]*count;
    for number in numbers:
        index=int(math.floor((number-origin)/width));
        if index<0: index=0;
        if index>=count: index=count-1;
        counts[index]+=1;
    xmin=[origin+i*width for i in range(count)]; xmax=[value+width for value in xmin]; centers=[value+width/2.0 for value in xmin]; total=float(len(numbers)); density=[value/(total*width) for value in counts];
    return {"x":tuple(centers),"count":tuple(float(v) for v in counts),"density":tuple(density),"width":width,"xmin":tuple(xmin),"xmax":tuple(xmax)};

def resolve(spec):
    layers=[];
    for layer in spec.layers:
        mappings=dict(spec.aes.mappings); mappings.update(dict(layer.aes.mappings)); params=dict(layer.params);
        if layer.stat=="bin" or layer.geom=="histogram":
            raw_x=evaluate(mappings.get("x",Literal([])),spec.data); computed=_bin(raw_x,params.get("binwidth"),params.get("bins"),params.get("boundary")); y_node=mappings.get("y");
            if isinstance(y_node,AfterStat): y=evaluate(y_node,spec.data,computed);
            elif y_node is None: y=computed["count"];
            else: y=evaluate(y_node,spec.data,computed);
            layers.append(ResolvedLayer("histogram",tuple(computed["x"]),tuple(y),(),(),layer.params,tuple(computed.items()))); continue;
        x=evaluate(mappings.get("x",Literal([])),spec.data); y=evaluate(mappings.get("y",Literal([])),spec.data); groups=evaluate(mappings.get("fill",mappings.get("color",Literal([]))),spec.data);
        if layer.geom in ("bar","bar3d") and layer.position=="stack" and groups:
            categories=[]; series={};
            for xv,yv,gv in zip(x,y,groups):
                if xv not in categories: categories.append(xv);
                series.setdefault(gv,{});
                for values in series.values(): values.setdefault(xv,0.0);
                series[gv][xv]=series[gv].get(xv,0.0)+float(yv);
            packed=tuple((str(group),tuple(values.get(cat,0.0) for cat in categories)) for group,values in series.items()); layers.append(ResolvedLayer(layer.geom,tuple(categories),(),tuple(groups),packed,layer.params));
        else: layers.append(ResolvedLayer(layer.geom,tuple(x) if isinstance(x,(list,tuple)) else (x,),tuple(y) if isinstance(y,(list,tuple)) else (y,),tuple(groups) if isinstance(groups,(list,tuple)) else (),(),layer.params));
    return ResolvedPlot(tuple(layers),spec.labels,spec.options);
