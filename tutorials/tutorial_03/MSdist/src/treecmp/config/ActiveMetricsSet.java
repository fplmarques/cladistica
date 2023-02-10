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

public class ActiveMetricsSet {

    private static ActiveMetricsSet AMset;
    private Vector<Metric> metricList;

    protected ActiveMetricsSet()
    {
        AMset=null;
        metricList=new Vector<Metric>();
        metricList.clear();

    }

    public static ActiveMetricsSet getActiveMetricsSet()
    {
        if(AMset==null)
        {
            AMset=new ActiveMetricsSet();
        }
        return AMset;
    }

    public void addMetric(Metric m)
    {

        /**
         *
         * Here can be added a protection against adding the same metric more than onec
         */

        this.metricList.add(m);

    }
    public Vector<Metric> getActiveMetrics()
    {

        return this.metricList;
    }

     public Metric[] getActiveMetricsTable()
    {
        int size=this.metricList.size();
        Metric[] mTable=new Metric[size];

        for(int i=0;i<size;i++)
        {
            mTable[i]=this.metricList.get(i);

        }


         return mTable;
    }


}
