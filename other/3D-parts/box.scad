/* use <MCAD/regular_shapes.scad> */

include <BOSL/nema_steppers.scad>
use <BOSL/nema_steppers.scad>

include <BOSL/constants.scad>
use <BOSL/metric_screws.scad>

include <ScrewsMetric/ScrewsMetric.scad>;
include <ScrewsMetric/Optional-Bearings.scad>;

box_lenght = 142;
box_width = 100;
box_height = 55;

box_border_width = 5;
box_pad_r = 20;
box_pad_h = 10;
box_pad_hole_r = 1.5;

box_gears_width = 30+5;

border_clearance = 5;
stepper_lenght = 48;
stepper_width = 42.3;
stepper_plinth = 2;

cover_height = 3;
cover_space_up = 2;

winder_lenght = 30;
winder_r = 15;
winder_clearance = 5;

bottom_relative = (-box_height + stepper_width)/2 + border_clearance;

/* box_cutter(); */
box();
/* lead(); */
elements();
/* tux(); */
/* text(); */

/* difference() {
  box();
  translate([box_lenght/2, -box_width/2, 0])
    cube([box_lenght+0.2, box_width+0.2, box_height+0.2], center=true);
} */

module box() {
  difference() {
    cube(size=[box_lenght, box_width, box_height], center=true);
    box_cutter();
    /* tux();
    text(); */
  }
}

module winder() { // -stepper_width +stepper_plinth - winder_lenght - winder_clearance -box_gears_width -2.5
  translate([-winder_lenght/2 +(box_lenght-box_border_width*2)/2 -box_gears_width-2.5-box_border_width - stepper_lenght -winder_clearance, -box_width/2+5 + box_border_width +stepper_width/2 +30 , bottom_relative])
    rotate([0,90,0])
      cylinder(r=winder_r, h=winder_lenght, center=true);
}

/* cable_hole(); */
cable_hole_r = 2;
module cable_hole() { // -stepper_width +stepper_plinth - winder_lenght - winder_clearance -box_gears_width -2.5
  color("green")
    translate([-winder_lenght/2 +(box_lenght-box_border_width*2)/2 -box_gears_width-2.5-box_border_width - stepper_lenght -winder_clearance,
          (-box_width+box_border_width)/2,
           bottom_relative-winder_r*3/4]) {
      rotate([0,90,90]) {
        cylinder(r=cable_hole_r, h=box_border_width+0.2, center=true);
      }
    }
}

module lead_slicing() {
    // lead slicing
    translate([0, box_border_width/4, box_height/2 + (-cover_space_up-cover_height/2)]) {
      difference() {
        color("green")
          cube(size=[box_lenght-box_border_width, box_width-box_border_width/2 +0.1, cover_height], center=true);

        color("blue")
          translate([0, -box_width/2-0.7, 0])
            rotate([-30,0,0])
              cube(size=[box_lenght, cover_height*2, cover_height*5], center=true);
        color("blue")
          translate([box_lenght/2-0.7, 0, 0])
            rotate([-30,0,90])
              cube(size=[box_lenght, cover_height*2, cover_height*5], center=true);
        color("blue")
          translate([-box_lenght/2+0.7, 0, 0])
            rotate([30,0,90])
              cube(size=[box_lenght, cover_height*2, cover_height*5], center=true);
      }

    }
}

module lead() {
  union() {
    translate([0, box_border_width/4, box_height/2 + (-cover_space_up-cover_height/2)]) {
      difference() {
        color("green")
          cube(size=[box_lenght-box_border_width-0.1, box_width-box_border_width/2, cover_height], center=true);

        color("blue")
          translate([0, -box_width/2-0.6, 0])
            rotate([-30,0,0])
              cube(size=[box_lenght, cover_height*2, cover_height*5], center=true);
        color("blue")
          translate([box_lenght/2-0.8, 0, 0])
            rotate([-30,0,90])
              cube(size=[box_lenght, cover_height*2, cover_height*5], center=true);
        color("blue")
          translate([-box_lenght/2+0.8, 0, 0])
            rotate([30,0,90])
              cube(size=[box_lenght, cover_height*2, cover_height*5], center=true);
      }

    }

    translate([0, box_border_width/2, box_height/2 + (-cover_space_up-cover_height)/2 +0.1]) {
      cube(size=[box_lenght-box_border_width*2-0.2, box_width-box_border_width, cover_space_up+cover_height], center=true);
    }

    text_chicken_coop();
    logo_chicken();
  }
}

module box_cutter() {
  color("red") {
    difference() {
      cube(size=[box_lenght-box_border_width*2, box_width-box_border_width*2, box_height+0.2], center=true);

      // Central separator
      translate([(box_lenght-box_border_width*2-box_border_width*2)/2-box_gears_width, 0, 0]) {
        difference() {
          cube(size=[box_border_width, box_width, box_height+0.3], center=true);
          // lead space
          translate([0, 0, box_height/2 + (-cover_space_up-cover_height)/2 +0.1]) {
            cube(size=[box_border_width+0.2, box_width+0.2, cover_space_up+cover_height+0.1], center=true);
          }
        }
      }

      // Pads
      translate([(box_lenght-box_border_width*2)/2, (box_width-box_border_width*2)/2, -box_height/2])
        cylinder(r=box_pad_r, h=box_pad_h, center=true);
      translate([(box_lenght-box_border_width*2)/2, -(box_width-box_border_width*2)/2, -box_height/2])
        cylinder(r=box_pad_r, h=box_pad_h, center=true);
      translate([-(box_lenght-box_border_width*2)/2, (box_width-box_border_width*2)/2, -box_height/2])
        cylinder(r=box_pad_r, h=box_pad_h, center=true);
      translate([-(box_lenght-box_border_width*2)/2, -(box_width-box_border_width*2)/2, -box_height/2])
        cylinder(r=box_pad_r, h=box_pad_h, center=true);
    }

    // lead space
    translate([0, box_width/2, box_height/2 + (-cover_space_up-cover_height)/2 +0.1]) {
      cube(size=[box_lenght-box_border_width*2, box_border_width*2+0.1, cover_space_up+cover_height+0.1], center=true);
    }

    // lead slicing
    lead_slicing();

    cable_hole();

    // Pads holes
    translate([(box_lenght-box_border_width*2)/2-box_pad_r/2.5, (box_width-box_border_width*2)/2-box_pad_r/2.5, -box_height/2])
      cylinder(r=box_pad_hole_r, h=box_pad_h+0.2, center=true);
    translate([(box_lenght-box_border_width*2)/2-box_pad_r/2.5, -(box_width-box_border_width*2)/2+box_pad_r/2.5, -box_height/2])
      cylinder(r=box_pad_hole_r, h=box_pad_h+0.2, center=true);
    translate([-(box_lenght-box_border_width*2)/2+box_pad_r/2.5, (box_width-box_border_width*2)/2-box_pad_r/2.5, -box_height/2])
      cylinder(r=box_pad_hole_r, h=box_pad_h+0.2, center=true);
    translate([-(box_lenght-box_border_width*2)/2+box_pad_r/2.5, -(box_width-box_border_width*2)/2+box_pad_r/2.5, -box_height/2])
      cylinder(r=box_pad_hole_r, h=box_pad_h+0.2, center=true);

    // motor mount
    translate([(box_lenght-box_border_width*2)/2-box_gears_width-box_border_width, -box_width/2 + box_border_width+5, bottom_relative])
      nema17_mount_holes(depth=5.2, l=0, orient=ORIENT_X, align=V_BACK);

    // bearings
    translate([(-box_lenght+box_border_width)/2, -box_width/2+5 + box_border_width +stepper_width/2 +30 , bottom_relative])
      rotate([0,90,0])
          cylinder(r=11, h=10, center=true);
    translate([(box_lenght-box_border_width*2)/2-box_gears_width-box_border_width, -box_width/2+5 + box_border_width +stepper_width/2 +30 , bottom_relative])
      rotate([0,90,0])
          cylinder(r=11, h=10, center=true);
  }
}


module elements() {
  // Gears
  color("cyan") {
  translate([(box_lenght-box_border_width*2)/2-box_gears_width+30, -box_width/2 + box_border_width+5 +30 +0.6, bottom_relative]) //-14.7
    rotate([90,180,-90])
      import("ParametricHerringboneGears.stl");
  }

  // stepper
  translate([(box_lenght-box_border_width*2)/2-box_gears_width-48+22-box_border_width, -box_width/2 + box_border_width+5, bottom_relative ])
      nema17_stepper(h=48, shaft_len=22, orient=ORIENT_X, align=V_BACK);

  // rod
  translate([-20, -box_width/2+5 + box_border_width +stepper_width/2 +30 , bottom_relative])
    rotate([0,90,0])
      cylinder(r=4, h=box_lenght-box_border_width, center=true);

  // nut
  rotate([0,0,0])
    translate([(box_lenght-box_border_width*2)/2-box_gears_width+30, -box_width/2+5 + box_border_width +stepper_width/2 +30 , bottom_relative -7.5])
      metric_nut(size=8, hole=true, pitch=1.5, details=true, orient=ORIENT_X);

  // bearings
  color("grey") {
    translate([(-box_lenght+box_border_width)/2-2.5, -box_width/2+5 + box_border_width +stepper_width/2 +30 , bottom_relative])
      rotate([0,90,0])
        BearingFromSize(M8);
    translate([(box_lenght-box_border_width*2)/2-box_gears_width-box_border_width-2.5, -box_width/2+5 + box_border_width +stepper_width/2 +30 , bottom_relative])
      rotate([0,90,0])
        BearingFromSize(M8);
  }
  winder();
}

module text() {
  _scale=1/3;
  color("purple")
  translate([box_lenght/2-box_border_width/8, -box_height/1.7, box_height/2 -5])
  scale([_scale, _scale, _scale])
  rotate([0, 90, 0])
  linear_extrude(height = 10, center = false, scale=1)
    import("thereisnoplacelike127.0.0.1.svg");
}

module text_chicken_coop() {
  _scale=3/4;
  color("purple")
  translate([29,20,  box_height/2-1])
  scale([_scale, _scale, 1])
  /* rotate([0, 90, 0]) */
  linear_extrude(height = 2, center = false, scale=1)
    import("chicken-text.svg", center=true);
}

module logo_chicken() {
  _scale=1/4;
  color("purple")
  translate([-15, 2,  box_height/2-1])
  scale([_scale, _scale, 1])
  /* rotate([0, 90, 0]) */
  linear_extrude(height = 3, center = false, scale=1)
    import("chicken-logo1.svg", center=true);
}

module tux() {
  _scale=1/8;
  color("black")
  translate([box_lenght/2+box_border_width/8, 0, 0-box_height/2 +12]) //-box_height/2 +12
  scale([_scale, _scale, _scale])
  rotate([90, -90, -90])
  difference()
  {
    linear_extrude(height = 10, center = false, scale=1)
      import("Tux_Mono-sub0.svg");
    translate([0, 0, -1])
    linear_extrude(height = 80, center = false, scale=1)
      import("Tux_Mono-sub1.svg");
    translate([0, 0, -1])
    difference() {
      linear_extrude(height = 80, center = false, scale=1)
        import("Tux_Mono-sub2.svg");
      translate([0, 0, -2])
        linear_extrude(height = 80, center = false, scale=1)
          import("Tux_Mono-sub2-1.svg");
    }
  }
}
