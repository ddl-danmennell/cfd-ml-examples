/*  This file is part of the OpenLB library
 *
 *  Copyright (C) 2016 Mathias J. Krause, Marie-Luise Maier
 *  E-mail contact: info@openlb.net
 *  The most recent release of OpenLB can be downloaded at
 *  <http://www.openlb.net/>
 *
 *  This program is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License
 *  as published by the Free Software Foundation; either version 2
 *  of the License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public
 *  License along with this program; if not, write to the Free
 *  Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
 *  Boston, MA  02110-1301, USA.
*/

#include "dynamics/latticeDescriptors.h"
#include "dynamics/latticeDescriptors.hh"
#include "particles/particle3D.h"
#include "particles/particle3D.hh"
#include "hertzMindlinDeresiewicz3D.h"
#include "hertzMindlinDeresiewicz3D.hh"

namespace olb {

template class HertzMindlinDeresiewicz3D<double,Particle3D,descriptors::D3Q19Descriptor>;
template class HertzMindlinDeresiewicz3D<double,MagneticParticle3D,descriptors::D3Q19Descriptor>;

}  // namespace olb
