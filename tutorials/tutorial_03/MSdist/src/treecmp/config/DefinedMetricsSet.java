/** This file is part of MSdist, a program for computing the Matching Split
    distance between phylogenetic trees.
    Copyright (C) 2010,  Damian Bogdanowicz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>. */

package treecmp.config;

import java.util.Vector;
import treecmp.metric.Metric;

public class DefinedMetricsSet {

    private static DefinedMetricsSet DMset;
    private Vector<Metric> metricList;
    
    protected DefinedMetricsSet()
    {
        DMset=null;
        metricList=new Vector<Metric>();
        metricList.clear();

    }
    
    public static DefinedMetricsSet getDefinedMetricsSet()
    {
        if(DMset==null)
        {
            DMset=new DefinedMetricsSet(); 
        }
        return DMset;
    }
         
    public void addMetric(Metric m)
    {

        /**
         *
         * Here can be added a protection against adding the same metric more than onec
         */

        this.metricList.add(m);

    }
    public Vector<Metric> getDefinedMetrics()
    {

        return this.metricList;
    }


}
