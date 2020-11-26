var postcss = require('gulp-postcss');
var gulp = require('gulp');
var autoprefixer = require('autoprefixer');
var tailwindcss = require('tailwindcss');

task = function() {
    var plugins = [
        tailwindcss,
        autoprefixer
    ];
    return gulp.src('./juliano/static/src/*.css')
        .pipe(postcss(plugins))
        .pipe(gulp.dest('./juliano/static/build/'));
};

exports.default = task
