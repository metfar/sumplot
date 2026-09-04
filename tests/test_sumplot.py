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
from sumplot import *;

def test_ast_not_eval():
    node=BinaryExpr("/",ColumnRef("hp"),ColumnRef("wt")); assert evaluate(node,{"hp":[10],"wt":[2]})==[5];
def test_stack():
    p=PlotSpec({"x":["A","A","B","B"],"y":[1,2,3,4],"g":["u","v","u","v"]},AesSpec.from_dict({"x":"x","y":"y","fill":"g"}),(LayerSpec("bar",position="stack"),)); r=resolve(p); assert r.layers[0].series[0][1]==(1.0,3.0);
def test_chart_adapter():
    p=PlotSpec({"x":["A"],"y":[2]},AesSpec.from_dict({"x":"x","y":"y"}),(LayerSpec("bar3d"),)); assert to_chart_spec(p).kind=="bar3d";
def test_after_stat_node(): assert isinstance(after_stat("density"),AfterStat);


def test_histogram_density():
    p=ggplot({"mpg":[10.2,10.8,11.1,12.4]},aes("mpg",after_stat("density")))+geom_histogram(binwidth=1,fill="#51A8C9"); r=resolve(p); layer=r.layers[0]; assert layer.geom=="histogram"; assert abs(sum(layer.y)*layer.computed_value("width")-1.0)<1e-12;

def test_histogram_chart_adapter_color():
    p=ggplot({"mpg":[10.2,10.8,11.1]},aes("mpg",after_stat("density")))+geom_histogram(binwidth=1,fill="#51A8C9"); chart=to_chart_spec(p); assert chart.kind=="bar"; assert chart.option("series_colors")==("#51A8C9",);

def test_ggsave_png(tmp_path,monkeypatch):
    monkeypatch.setenv("MPLBACKEND","Agg"); p=ggplot({"mpg":[10.2,10.8,11.1]},aes("mpg",after_stat("density")))+geom_histogram(binwidth=1,fill="#51A8C9"); target=tmp_path/"hist.png"; ggsave(target,p,width=4,height=3,dpi=80); assert target.read_bytes()[:8]==b"\x89PNG\r\n\x1a\n";

def test_cli_version(capsys):
    from sumplot.cli import main; import pytest;
    with pytest.raises(SystemExit) as exc: main(["--version"]);
    assert exc.value.code==0; assert "sumplot 0.1.0a2" in capsys.readouterr().out;
