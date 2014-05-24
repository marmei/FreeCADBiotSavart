/* adapted from FRAME3DD: Static and dynamic structural analysis of 2D & 3D frames and trusses
Copyright (C) 2007-2008 John Pye
2012      Markus Meissner for Gradient Simulator  

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

typedef struct vec3_struct {
  double x, y, z;
} vec3;

vec3 vec3_create(double x, double y, double z) {
  vec3 A;
  A.x = x; A.y = y; A.z = z;
  return A;
}

vec3 vec3_add(vec3 A, vec3 B) {
  return vec3_create (
		      A.x+B.x, A.y + B.y, A.z + B.z
		      );
}

vec3 vec3_cross(vec3 a, vec3 b) {
  return vec3_create (
		      a.y*b.z-a.z*b.y,
		      a.z*b.x-a.x*b.z,
		      a.x*b.y-a.y*b.x
		      );
}

double vec3_abs(vec3 a) {
  return sqrt(pow(a.x,2) + pow(a.y,2) + pow(a.z,2));
}

vec3 vec3_negate(vec3 A) {
  vec3 B;
  B.x = -A.x;
  B.y = -A.y;
  B.z = -A.z;
  return B;
}

vec3 vec3_diff(vec3 A, vec3 B){
  return vec3_create(A.x - B.x, A.y - B.y, A.z - B.z);
}

vec3 vec3_scale(vec3 A, double s){
  return vec3_create(A.x * s, A.y * s, A.z * s);
}
