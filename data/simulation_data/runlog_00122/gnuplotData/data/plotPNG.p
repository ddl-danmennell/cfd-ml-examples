set key bottom right
set terminal png
set output '/mnt/code/data/simulation_data/runlog_00122/gnuplotData/drag.png'
plot '/mnt/code/data/simulation_data/runlog_00122/gnuplotData/data/drag.dat' u 1:2 w l t 'drag(openLB)'
