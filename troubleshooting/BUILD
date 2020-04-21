load("@io_bazel_rules_python//python:python.bzl", "py_library", "py_test")

load("@graknlabs_client_python_pip//:requirements.bzl",
       graknlabs_client_python_requirement = "requirement")

py_library(
    name = "troubleshooting",
    srcs = ["troubleshooting.py"],
    deps = [
        "@graknlabs_client_python//:client_python",
        ":migration",
    ],
)

py_library(
    name = "migration",
    srcs = [
        "migration.py",
        "templates.py",
    ],
    deps = [
        "@graknlabs_client_python//:client_python"
    ],
    data = [
        "//schemas:troubleshooting-schema.gql"
    ]
)

py_test(
    name = "test_E2E",
    main = "test_E2E.py",
    srcs = [
        "test_E2E.py",
#        ":migration",
    ],
    deps = [
        "@graknlabs_client_python//:client_python",
        ":troubleshooting",
        ":migration",
    ],
    data = [
        "//schemas:troubleshooting-schema.gql"
    ]
)

#py_binary(
#    name = "app",
#    srcs = ["src/app.py"],
##    data = [":transform"],  # a cc_binary which we invoke at run time
#    deps = [
#        "@graknlabs_client_python//:client_python"
#    ]
#)