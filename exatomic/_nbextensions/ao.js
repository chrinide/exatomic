/*"""
==================
ao.js
==================
*/
'use strict';


require.config({
    shim: {
        'nbextensions/exa/field': {
            exports: 'field'
        },
    },
});


define([
    'nbextensions/exa/field'
], function(field) {
    class AO extends field.ScalarField {
        /*"""
        AO
        ----------
        */
        constructor(dimensions, which) {
            super(dimensions, hydrogen[which]);
            //this.function = which;
        };
    };

    var hydrogen = {
        '1s': function(x, y, z) {
            var r = Math.sqrt(x * x + y * y + z * z);
            var Z = 1;
            var sigma = Z * r
            return 1 / Math.sqrt(Math.PI) * Math.pow(Z, 3/2) * Math.exp(-sigma);
        },

        '2s': function(x, y, z) {
            var r = Math.sqrt(x * x + y * y + z * z);
            var Z = 1;
            var sigma = Z * r
            var norm = 1 / (4 * Math.sqrt(2 * Math.PI)) * Math.pow(Z, 3/2)
            return norm * (2 - sigma) * Math.exp(-sigma / 2);
        },

        '2pz': function(x, y, z) {
            var r = Math.sqrt(x * x + y * y + z * z);
            var Z = 1;
            var sigma = Z * r
            var norm = 1 / (4 * Math.sqrt(2 * Math.PI)) * Math.pow(Z, 3/2)
            return norm * Z * z * Math.exp(-sigma / 2);
        },

        '2px': function(x, y, z) {
            var r = Math.sqrt(x * x + y * y + z * z);
            var Z = 1;
            var sigma = Z * r
            var norm = 1 / (4 * Math.sqrt(2 * Math.PI)) * Math.pow(Z, 3/2)
            return norm * Z * x * Math.exp(-sigma / 2);
        },

        '2py': function(x, y, z) {
            var r = Math.sqrt(x * x + y * y + z * z);
            var Z = 1;
            var sigma = Z * r
            var norm = 1 / (4 * Math.sqrt(2 * Math.PI)) * Math.pow(Z, 3/2)
            return norm * Z * y * Math.exp(-sigma / 2);
        },

        '3s': function(x, y, z) {
            var r = Math.sqrt(x * x + y * y + z * z);
            var Z = 1;
            var sigma = Z * r
            var norm = 1 / (81 * Math.sqrt(3 * Math.PI)) * Math.pow(Z, 3/2)
            var prefac = (27 - 18 * sigma + 2 * Math.pow(sigma, 2))
            return norm * prefac * Math.exp(-sigma / 3);
        },

        '3pz': function(x, y, z) {
            var r = Math.sqrt(x * x + y * y + z * z);
            var Z = 1;
            var sigma = Z * r
            var norm = Math.sqrt(2) / (81 * Math.sqrt(Math.PI)) * Math.pow(Z, 3/2)
            var prefac = Z * (6 - sigma)
            return norm * prefac * z * Math.exp(-sigma / 3);
        },

        '3py': function(x, y, z) {
            var r = Math.sqrt(x * x + y * y + z * z);
            var Z = 1;
            var sigma = Z * r
            var norm = Math.sqrt(2) / (81 * Math.sqrt(Math.PI)) * Math.pow(Z, 3/2)
            var prefac = Z * (6 - sigma)
            return norm * prefac * y * Math.exp(-sigma / 3);
        },

        '3px': function(x, y, z) {
            var r = Math.sqrt(x * x + y * y + z * z);
            var Z = 1;
            var sigma = Z * r
            var norm = Math.sqrt(2) / (81 * Math.sqrt(Math.PI)) * Math.pow(Z, 3/2)
            var prefac = Z * (6 - sigma)
            return norm * prefac * x * Math.exp(-sigma / 3);
        },

        '3d0': function(x, y, z) {
            var z2 = z * z;
            var r = Math.sqrt(x * x + y * y + z2);
            var r2 = r * r;
            var Z = 1;
            var sigma = Z * r;
            var ynorm = Math.sqrt(5 / (16 * Math.PI));
            var ybody = (3 * z2 / r2 - 1);
            var rnorm = 1 / Math.sqrt(2430);
            var rbody = Math.pow(Z, 3 / 2) * Math.pow(2 / 3 * sigma, 2) * Math.exp(-sigma / 3);
            return ynorm * rnorm * ybody * rbody;
        },

        '3d+1': function(x, y, z) {
            var x2 = x * x;
            var y2 = y * y;
            var z2 = z * z;
            var r2 = x2 + y2 + z2;
            var r = Math.sqrt(r2);
            var Z = 1;
            var sigma = Z * r;
            var ynorm = -Math.sqrt(15 / (8 * Math.PI));
            var ymix = 2 / Math.sqrt(2) * z / r * Math.sqrt(1 - z2 / r2) * y / (x * Math.sqrt(y2 / x2 + 1));
            var rnorm = 1 / Math.sqrt(2430);
            var rbody = Math.pow(Z, 3 / 2) * Math.pow(2 / 3 * sigma, 2) * Math.exp(-sigma / 3);
            return ynorm * rnorm * ymix * rbody;
        },

        '3d-1': function(x, y, z) {
            var sigma = Z * r;
            var x2 = x * x;
            var y2 = y * y;
            var z2 = z * z;
            var r2 = x2 + y2 + z2;
            var r = Math.sqrt(r2);
            var Z = 1;
            var sigma = Z * r;
            var ynorm = Math.sqrt(15 / (8 * Math.PI));
            var ymix = -2 / Math.sqrt(2) * z / r * Math.sqrt(1 - (z2/(r2))) * 1 / Math.sqrt(x2/y2 + 1);
            var rnorm = 1 / Math.sqrt(2430);
            var rbody = Math.pow(Z, 3 / 2) * Math.pow(2 / 3 * sigma, 2) * Math.exp(-sigma / 3);
            return ynorm * rnorm * ymix * rbody;
        },

        '3d+2': function(x, y, z) {
            var sigma = Z * r;
            var x2 = x * x;
            var y2 = y * y;
            var z2 = z * z;
            var r2 = x2 + y2 + z2;
            var r = Math.sqrt(r2);
            var Z = 1;
            var sigma = Z * r;
            var ynorm = Math.sqrt(15 / (32 * Math.PI));
            var ymix = 2 / Math.sqrt(2) * (1 - z2/r2) * (x2 - y2)/(x2 + y2);
            var rnorm = 1 / Math.sqrt(2430);
            var rbody = Math.pow(Z, 3 / 2) * Math.pow(2 / 3 * sigma, 2) * Math.exp(-sigma / 3);
            return ynorm * rnorm * ymix * rbody;
        },

        '3d-2': function(x, y, z) {
            var x2 = x * x;
            var y2 = y * y;
            var z2 = z * z;
            var r2 = x2 + y2 + z2;
            var r = Math.sqrt(r2);
            var Z = 1;
            var sigma = Z * r;
            var ynorm = Math.sqrt(15 / (32 * Math.PI));
            var ymix = 2 / Math.sqrt(2) * (1 - z2/r2) * 2 * x * y / (x2 + y2);
            var rnorm = 1 / Math.sqrt(2430);
            var rbody = Math.pow(Z, 3 / 2) * Math.pow(sigma, 2) * Math.exp(-sigma / 3);
            return ynorm * rnorm * ymix * rbody;
        },

        '3dz2': function(x, y, z) {
            var r = Math.sqrt(x * x + y * y + z * z);
            var Z = 1;
            var sigma = Z * r;
            var norm = 1 / (81 * Math.sqrt(6 * Math.PI)) * Math.pow(Z, 3/2);
            var prefac = Math.pow(sigma, 2) * (3 * Math.pow(z / r, 2) - 1);
            return norm * prefac * Math.exp(-sigma / 3);
        },
        
        '3dxz': function(x, y, z) {
            var x2 = x * x;
            var y2 = y * y;
            var z2 = z * z;
            var r2 = x2 + y2 + z2;
            var r = Math.sqrt(r2);
            var Z = 1;
            var sigma = Z * r;
            var norm = Math.sqrt(2) / (81 * Math.sqrt(Math.PI)) * Math.pow(Z, 3/2);
            var prefac = Math.pow(Z, 2) * x2 * (r2 - z2) / (y2 * Math.sqrt((x2 + y2) / y2));
            return norm * prefac * Math.exp(-sigma / 3);
        },

        '3dyz': function(x, y, z) {
            var x2 = x * x;
            var y2 = y * y;
            var z2 = z * z;
            var r2 = x2 + y2 + z2;
            var r = Math.sqrt(r2);
            var Z = 1;
            var sigma = Z * r;
            var norm = Math.sqrt(2) / (81 * Math.sqrt(Math.PI)) * Math.pow(Z, 3/2);
            var prefac = Math.pow(Z, 2) * x * (r2 - z2) / (y * Math.sqrt((x2 + y2) / y2));
            return norm * prefac * Math.exp(-sigma / 3);
        },

        '3dx2-y2': function(x, y, z) {
            var x2 = x * x;
            var y2 = y * y;
            var z2 = z * z;
            var r2 = x2 + y2 + z2;
            var r = Math.sqrt(r2);
            var Z = 1;
            var sigma = Z * r;
            var norm = Math.sqrt(2) / (81 * Math.sqrt(Math.PI)) * Math.pow(Z, 3/2);
            var prefac = Math.pow(Z, 2) * (r2 - z2) * (x2 - y2) / (x2 + y2);
            return norm * prefac * Math.exp(-sigma / 3);
        },

        '3dxy': function(x, y, z) {
            var x2 = x * x;
            var y2 = y * y;
            var z2 = z * z;
            var r2 = x2 + y2 + z2;
            var r = Math.sqrt(r2);
            var Z = 1;
            var sigma = Z * r;
            var norm = Math.sqrt(2) / (81 * Math.sqrt(Math.PI)) * Math.pow(Z, 3/2);
            var prefac = Math.pow(Z, 2) * 2 * x * y * (r2 - z2) /(x2 + y2);
            return norm * prefac * Math.exp(-sigma / 3);
        },

    };

    return AO;
});
