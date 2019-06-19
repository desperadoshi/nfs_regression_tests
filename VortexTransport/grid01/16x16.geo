cell_x = 16;
cell_y = 16;
npts_x = cell_x + 1;
npts_y = cell_y + 1;
ratio_x = 1.0;
ratio_y = 1.0;

Lx = 0.1;
Ly = 0.1;

Point(1) = {0.0,0.0, 0};
Point(2) = { Lx,0.0, 0};
Point(3) = { Lx, Ly, 0};
Point(4) = {0.0, Ly, 0};

Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};

Transfinite Line {1, 3} = npts_x Using Progression ratio_x;
Transfinite Line {2, 4} = npts_y Using Progression ratio_y;

Line Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};

Transfinite Surface {1};
Recombine Surface {1};

Physical Line("Periodic-1") = {1};
Physical Line("Periodic-2") = {3};
Physical Line("Periodic-3") = {2};
Physical Line("Periodic-4") = {4};
Physical Surface("Fluids") = {1};

Mesh 2;
Save "16x16.msh";
