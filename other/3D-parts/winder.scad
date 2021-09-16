include <ScrewsMetric/ScrewsMetric.scad>;

include <BOSL/constants.scad>
use <BOSL/metric_screws.scad>

$fn=80;

winder_lenght = 30;
winder_r = 15;
rod_r = 4;

line_r = 1.5;

difference() {
  rotate_extrude(angle=360)
  import("winder.svg");

  color("blue")
    translate([0, 0, winder_lenght/2])
      cylinder(r=rod_r+0.2, h=winder_lenght+0.2, center=true);

  rotate([0, 0, 23])
    metric_nut(8, hole=false);

  // line hole
  rotate_extrude(angle=-15)
    import("winder-hole.svg");

  /* // cutter
  translate([-winder_r, 0, 0])
    cube([winder_r*2,winder_r*2,winder_lenght+0.2]); */
}

  /* color("red")
    translate([rod_r+line_r/2+1.5, 0, winder_lenght/2])
      cylinder(r=line_r, h=winder_lenght+0.2, center=true); */
