set key bottom right
set terminal pdf enhanced
set output '/mnt/code/data/simulation_data/runlog_00112/gnuplotData/drag.pdf'
plot '/mnt/code/data/simulation_data/runlog_00112/gnuplotData/data/drag.dat' u 1:2 w l t 'drag(openLB)'
