/*  This file is part of the OpenLB library
 *
 *  Copyright (C) 2006, 2007 Jonas Latt
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

/** \file
 * Helper functions for the implementation of MRT (multiple relaxation
 * time) dynamics. This file is all about efficiency.
 * The generic template code is specialized for commonly used Lattices,
 * so that a maximum performance can be taken out of each case.
 */
#ifndef D3Q13_HELPERS_H
#define D3Q13_HELPERS_H

#include "latticeDescriptors.h"
#include "core/cell.h"
#include "core/util.h"


namespace olb {

/// Helper functions for the (somewhat special) D3Q13 lattice
template<typename T>
struct d3q13Helpers {
  typedef descriptors::D3Q13Descriptor<T> Lattice;

  /// BGK collision step
  static T collision( Cell<T,descriptors::D3Q13Descriptor>& cell,
                      T rho, const T u[Lattice::d],
                      T lambda_nu, T lambda_nu_prime)
  {
    const T lambda_e = descriptors::D3Q13Descriptor<T>::lambda_e;
    const T lambda_h = descriptors::D3Q13Descriptor<T>::lambda_h;

    T uxSqr = util::sqr(u[0]);
    T uySqr = util::sqr(u[1]);
    T uzSqr = util::sqr(u[2]);
    T uSqr = uxSqr + uySqr + uzSqr;

    T s1 = cell[7] + cell[8] + cell[9] + cell[10];
    T s2 = cell[11] + cell[12];
    T s3 = cell[1] + cell[2] + cell[3] + cell[4];
    T s4 = cell[5] + cell[6];
    T sTot = s1 + s2 + s3 + s4;
    T d1 = cell[7] + cell[8] - cell[9] - cell[10];
    T d2 = cell[1] + cell[2] - cell[3] - cell[4];

    T M[13]; // The terms M[0]-M[3] are not used (they correspond
    // to rho, rho*ux, rho*uy, rho*uz respectively),
    // but we still use a 13-component vector to preserve
    // the clarity of the code.
    M[4] = -(T)12*cell[0] + sTot - (T)11/(T)2;
    // The 11/2 correction term in M4 accounts for the fact that
    // cell[i] corresponds to f[i]-ti, and not f[i]
    M[5] = s1 - (T)2*s2 + s3 - (T)2*s4;
    M[6] = d1 + d2;
    M[7] = cell[7] - cell[8] + cell[1] - cell[2];
    M[8] = cell[11] - cell[12] + cell[5] - cell[6];
    M[9] = cell[9] - cell[10] + cell[3] - cell[4];
    M[10] = d1 - d2;
    M[11] = -cell[7] + cell[8] + s2 + cell[1] - cell[2] - s4;
    M[12] = cell[9] - cell[10] - cell[11] + cell[12]
            - cell[3] + cell[4] + cell[5] - cell[6];
    T Mneq[13]; // The terms Mneq[0]-Mneq[3] are not used (they are
    // actually all zero, because of conservation laws),
    // but we still use a 13-component vector to preserve
    // the clarity of the code.
    Mneq[4] = M[4] + (T)11/(T)2*rho - (T)13/(T)2*rho*uSqr;
    Mneq[5] = M[5] - rho*( (T)2*uxSqr-(uySqr+uzSqr) );
    Mneq[6] = M[6] - rho*( uySqr-uzSqr );
    Mneq[7] = M[7] - rho*( u[0]*u[1] );
    Mneq[8] = M[8] - rho*( u[1]*u[2] );
    Mneq[9] = M[9] - rho*( u[0]*u[2] );
    Mneq[10] = M[10];
    Mneq[11] = M[11];
    Mneq[12] = M[12];

    Mneq[4]  *= lambda_e  / (T)156;
    Mneq[5]  *= lambda_nu / (T)24;
    Mneq[6]  *= lambda_nu / (T)8;
    Mneq[7]  *= lambda_nu_prime / (T)4;
    Mneq[8]  *= lambda_nu_prime / (T)4;
    Mneq[9]  *= lambda_nu_prime / (T)4;
    Mneq[10] *= lambda_h / (T)8;
    Mneq[11] *= lambda_h / (T)8;
    Mneq[12] *= lambda_h / (T)8;

    T F1 = Mneq[4] + Mneq[5] + Mneq[6];
    T F2 = Mneq[4] + Mneq[5] - Mneq[6];
    T F3 = Mneq[4] - (T)2*Mneq[5];

    cell[0]  -= (T)-12*Mneq[4];
    cell[1]  -= F1 + Mneq[7]                -Mneq[10]+Mneq[11];
    cell[2]  -= F1 - Mneq[7]                -Mneq[10]-Mneq[11];
    cell[3]  -= F2                  +Mneq[9]+Mneq[10]         -Mneq[12];
    cell[4]  -= F2                  -Mneq[9]+Mneq[10]         +Mneq[12];
    cell[5]  -= F3          +Mneq[8]                 -Mneq[11]+Mneq[12];
    cell[6]  -= F3          -Mneq[8]                 -Mneq[11]-Mneq[12];
    cell[7]  -= F1 + Mneq[7]                +Mneq[10]-Mneq[11];
    cell[8]  -= F1 - Mneq[7]                +Mneq[10]+Mneq[11];
    cell[9]  -= F2                  +Mneq[9]-Mneq[10]         +Mneq[12];
    cell[10] -= F2                  -Mneq[9]-Mneq[10]         -Mneq[12];
    cell[11] -= F3          +Mneq[8]                 +Mneq[11]-Mneq[12];
    cell[12] -= F3          -Mneq[8]                 +Mneq[11]+Mneq[12];

    return uSqr;
  }

  /// BGK collision step with density correction
  static T constRhoCollision( Cell<T,descriptors::D3Q13Descriptor>& cell,
                              T rho, const T u[Lattice::d],
                              T ratioRho,
                              T lambda_nu, T lambda_nu_prime)
  {
    const T uSqr = util::normSqr<T,Lattice::d>(u);

    return uSqr;
  }
}; // struct d3q13helpers

}  // namespace olb

#endif
