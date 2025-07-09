This is the code that creates gravitational wave with Blender. 
The details of how to run the code is include in the README.pdf

To run the script, you need
1) VTK data of the waves
2) Density movie made by visit (Optional)
3) Black hole radius if horizon data is missing (Optional)


To generate a movie, you want
1) convert VTK data to obj files. 
    i. use convert_vtk_to_obj_mememory.py if the VTK data has more than one set of data
    ii. use convert_vtk_to_obj.py if the VTK data only has one set of data
    iii. make_obj.py is very basic and doesn't cut a hole

2) (Optional) Create memory map by running 
    i. createmap.py if you want memory
    ii. createmap_r.py if you want r*memory

3) (Optional) Generated the black holes radius data if the horizon data is missing from Visit
    run generate_bh.py in bh_data. Make sure you have BH_diagnostics.ah1.gp before running


4) run .runSingle with parameters changed to fit the data
