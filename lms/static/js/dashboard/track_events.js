/**
 * Track the different click events on dashboard.
 */

var edx = edx || {};

(function ($, analytics) {
    'use strict';

    $(document).ready(function () {
        var course_title_link = $(".course-title-link"),
            course_image_link = $(".dashboard-course-image"),
            enter_course_link = $(".enter-course-link"),
            course_action_more = $(".wrapper-action-more"),
            course_action_upgrade = $(".action-upgrade"),
            find_courses_btn = $(".btn-find-courses"),
            course_learn_verified = $(".learned-verified-track");

        // Fire analytics events when the "course title link" button is clicked.
        course_title_link.on("click", function (event) {
            var courseKey = $(event.target).data("course-key");
            analytics.track(
                "edx.bi.dashboard.clicked_course_title_link",
                {
                    category: "dashboard",
                    label: courseKey
                }
            );
        });

        // Fire analytics events when the "course image" is clicked.
        course_image_link.on("click", function (event) {
            var courseKey = $(event.target).parent().data("course-key");
            analytics.track(
                "edx.bi.dashboard.clicked_course_image",
                {
                    category: "dashboard",
                    label: courseKey
                }
            );
        });

        // Fire analytics events when the "View Course" button is clicked.
        enter_course_link.on("click", function (event) {
            var courseKey = $(event.target).data("course-key");
            analytics.track(
                "edx.bi.dashboard.clicked_enter_course_link",
                {
                    category: "dashboard",
                    label: courseKey
                }
            );
        });

        // Fire analytics events when the "Settings" button is clicked.
        course_action_more.on("click", function (event) {
            var courseKey = $(event.target).parent().data("course-key");
            // If the user clicked on the fa-cog icon then change the don hierarchy.
            if(courseKey == undefined){
                courseKey = $(event.target).parent().parent().data("course-key");
            }
            event.stopPropagation();
            analytics.track(
                "edx.bi.dashboard.clicked_more_action",
                {
                    category: "dashboard",
                    label: courseKey
                }
            );
        });

        // Fire analytics events when the "Upgrade" button is clicked.
        course_action_upgrade.on("click", function (event) {
            var courseKey = $(event.target).parent().parent().data("course-id");
            analytics.track(
                "edx.bi.dashboard.clicked_course_upgrade_link",
                {
                    category: "dashboard",
                    label: courseKey
                }
            );
        });

        // Fire analytics events when the "Learned about verified track" link is clicked.
        course_learn_verified.on("click", function (event) {
            var courseKey = $(event.target).data("course-key");
            analytics.track(
                "edx.bi.dashboard.clicked_learned_verified_link",
                {
                    category: "dashboard",
                    label: courseKey
                }
            );
        });

        // Fire analytics events when the "Find Courses" button is clicked.
        find_courses_btn.on("click", function (event) {
            analytics.track(
                "edx.bi.dashboard.clicked_enter_course_link",
                {
                    category: "dashboard",
                    label: "edx_find_new_courses_button"
                }
            );
        });
    });
})(jQuery, window.analytics);

