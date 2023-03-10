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

package treecmp.metric;

import java.util.BitSet;
import pal.tree.SplitSystem;

public class SplitDist {

    /** Creates a new instance of SplitDist */
    public SplitDist() {
    }

    //dist([A1|A2],[B1|B2])=0.5*min((A1 xor B1)+(A2 xor B2),(A1 xor B2)+(A2 xor B1))
    public static double getDist1(boolean[] split1, boolean[] split2) {
        int n = split1.length;
        int eq = 0, neq = 0, q;
        double metric = 0.0;

        for (int i = 0; i < n; i++) {
            if (split1[i] == split2[i]) {
                eq++;
            } else {
                neq++;
            }
        }

        if (eq > neq) {
            q = eq;
        } else {
            q = neq;
        }

        return (double) (n - q);
    }

    public static int getDist1Int(boolean[] split1, boolean[] split2) {
        int n = split1.length;
        int eq = 0, neq = 0, q;

        for (int i = 0; i < n; i++) {
            if (split1[i] == split2[i]) {
                eq++;
            } else {
                neq++;
            }
        }

        if (eq > neq) {
            q = eq;
        } else {
            q = neq;
        }

        return (n - q);
    }

    public static double getNLGDist(boolean[] split1, boolean[] split2) {

        int n = split1.length;
        int eq_tt = 0, eq_ff = 0, eq_tf = 0, eq_ft = 0;
        double metric = 0.0;

        int s1_true;
        int s1_false;

        int s2_true;
        int s2_false;

        double a00, a11, a10, a01;

        s1_true = 0;
        s2_true = 0;
        eq_tt = 0;
        eq_ff = 0;
        eq_tf = 0;
        eq_ff = 0;

        for (int i = 0; i < n; i++) {
            if (split1[i] == true) {
                s1_true++;
            }

            if (split2[i] == true) {
                s2_true++;
            }

            if (split1[i] == true && split2[i] == true) {
                eq_tt++;
            }

            if (split1[i] == false && split2[i] == false) {
                eq_ff++;
            }

            if (split1[i] == true && split2[i] == false) {
                eq_tf++;
            }

            if (split1[i] == false && split2[i] == true) {
                eq_ft++;
            }
        }

        s1_false = n - s1_true;
        s2_false = n - s2_true;

        a00 = (double) eq_tt / (double) (s1_true + s2_true - eq_tt);
        a11 = (double) eq_ff / (double) (s1_false + s2_false - eq_ff);

        a01 = (double) eq_tf / (double) (s1_true + s2_false - eq_tf);

        a10 = (double) eq_ft / (double) (s1_false + s2_true - eq_ft);

        //max{min{a00,a11},min{a01,a10}}

        double a0011, a0110, a;

        if (a00 < a11) {
            a0011 = a00;
        } else {
            a0011 = a11;
        }

        if (a01 < a10) {
            a0110 = a01;
        } else {
            a0110 = a10;
        }

        if (a0011 > a0110) {
            a = a0011;
        } else {
            a = a0110;
        }

        return a;

    }

    public static double getDistToO_1(boolean[] split) {
        int n = split.length;

        return Math.ceil(Math.floor(n / 2.0) / 2.0);

    }

    public static double getDistToO_2(boolean[] split) {
        int n = split.length;
        int s_true = 0;

        for (int i = 0; i < n; i++) {
            if (split[i] == true) {
                s_true++;
            }
        }

        return Math.min(s_true, n - s_true);

    }

    public static int getMinSize(boolean[] split) {

        int n = split.length;
        int s_true = 0;

        for (int i = 0; i < n; i++) {
            if (split[i] == true) {
                s_true++;
            }
        }
        return Math.min(s_true, n - s_true);
    }

    public static int getMaxSize(boolean[] split) {
        int n = split.length;
        int max = n - getMinSize(split);

        return max;
    }

    public static int getDist1Bit(BitSet split1, BitSet split2, int n) {
        BitSet temp = (BitSet) split1.clone();

        temp.xor(split2);

        int neq = temp.cardinality();
        int eq = n - neq;
        int d;

        if (neq < eq) {
            d = neq;
        } else {
            d = eq;
        }
        return d;
    }

    public static int getDistToOAsMinBit(BitSet split, int n) {

        int t = split.cardinality();
        int f = n - t;
        int d;

        if (t < f) {
            d = t;
        } else {
            d = f;
        }

        return d;
    }

    public static int getDistToOAsN4Bit(BitSet split, int n) {
        return (int) Math.ceil(Math.floor(n / 2.0) / 2.0);
    }

    public static BitSet[] SplitSystem2BitSetArray(SplitSystem s) {
        int N = s.getSplitCount();

        BitSet[] bsA = new BitSet[N];
        int n = s.getLabelCount();
        boolean[] split;

        for (int i = 0; i < N; i++) {
            bsA[i] = new BitSet(n);
            split = s.getSplit(i);
            for (int j = 0; j < n; j++) {
                if (split[j] == true) {
                    bsA[i].set(j);
                }
            }
        }

        return bsA;
    }
}
