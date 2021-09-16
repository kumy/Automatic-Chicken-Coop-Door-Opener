
import("InfraredRingHolder-NoSupport.stl");

  translate([-25/2, 28, 0])
    cube([25,25,2], center=false);

/* difference() {
  rotate([0, -90, 0])
    import("case.stl");

  translate([0, 0, -11.001])
    cube([60,40,10], center=true);
} */
