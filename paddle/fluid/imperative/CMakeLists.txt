cc_library(
  imperative_flag
  SRCS flags.cc
  DEPS gflags flags)
cc_library(
  var_helper
  SRCS var_helper.cc
  DEPS tensor selected_rows extended_tensor)
if(WITH_XPU)
  cc_library(
    prepared_operator
    SRCS prepared_operator.cc
    DEPS xpu_op_list
         proto_desc
         operator
         device_context
         lod_tensor
         selected_rows_utils
         var_type_traits
         op_kernel_type
         data_transform
         nan_inf_utils
         scalar
         int_array
         var_helper
         profiler
         place)
else()
  cc_library(
    prepared_operator
    SRCS prepared_operator.cc
    DEPS proto_desc
         operator
         device_context
         lod_tensor
         selected_rows_utils
         var_type_traits
         op_kernel_type
         data_transform
         nan_inf_utils
         scalar
         int_array
         var_helper
         profiler
         place)
endif()
cc_library(
  layer
  SRCS layer.cc
  DEPS prepared_operator math_function imperative_flag variable_helper
       op_registry var_helper)
add_subdirectory(jit)
if(WITH_GPU)
  cc_library(
    layout_autotune
    SRCS layout_autotune.cc
    DEPS op_info phi_backends)
else()
  cc_library(
    layout_autotune
    SRCS layout_autotune.cc
    DEPS op_info)
endif()
cc_library(
  amp
  SRCS amp_auto_cast.cc
  DEPS layer var_helper)
cc_library(
  tracer
  SRCS tracer.cc
  DEPS layer
       engine
       program_desc_tracer
       amp
       denormal
       garbage_collector
       var_helper
       layout_autotune
       ops_extra_info)
cc_library(
  basic_engine
  SRCS basic_engine.cc
  DEPS layer gradient_accumulator switch_autotune)
cc_library(
  engine
  SRCS basic_engine.cc partial_grad_engine.cc
  DEPS layer gradient_accumulator switch_autotune)
cc_library(
  imperative_profiler
  SRCS profiler.cc
  DEPS flags)
if(NOT WIN32)
  if(WITH_NCCL OR WITH_RCCL)
    cc_library(
      imperative_all_reduce
      SRCS all_reduce.cc
      DEPS collective_helper device_context selected_rows_utils tensor)
    cc_library(
      nccl_context
      SRCS nccl_context.cc
      DEPS collective_helper device_context imperative_all_reduce
           var_type_traits)
    if(WITH_NCCL)
      nv_library(
        reducer
        SRCS reducer.cc reducer.cu
        DEPS layer imperative_all_reduce)
    endif()
    if(WITH_RCCL)
      hip_library(
        reducer
        SRCS reducer.cc reducer.cu
        DEPS layer imperative_all_reduce)
    endif()
  endif()
  if(WITH_XPU_BKCL)
    cc_library(
      bkcl_context
      SRCS bkcl_context.cc
      DEPS collective_helper device_context tensor var_type_traits)
    cc_library(
      reducer
      SRCS reducer.cc
      DEPS layer)
  endif()
  if(WITH_CNCL)
    cc_library(
      cncl_context
      SRCS cncl_context.cc
      DEPS collective_helper device_context tensor var_type_traits)
    cc_library(
      reducer
      SRCS reducer.cc
      DEPS layer)
  endif()
  if(WITH_NCCL
     OR WITH_RCCL
     OR WITH_XPU_BKCL)
    cc_library(
      heter_ccl_context
      SRCS heter_ccl_context.cc
      DEPS collective_helper device_context tensor var_type_traits)
  endif()
  cc_library(
    data_loader
    SRCS data_loader.cc
    DEPS enforce)
endif()
if(WITH_GLOO)
  cc_library(
    imperative_gloo_context
    SRCS gloo_context.cc
    DEPS collective_helper device_context tensor var_type_traits)
  if(WIN32
     OR (NOT
         (WITH_NCCL
          OR WITH_RCCL
          OR WITH_XPU_BKCL
          OR WITH_CNCL)
        ))
    cc_library(
      reducer
      SRCS reducer.cc
      DEPS layer)
  endif()
endif()

cc_library(
  gradient_accumulator
  SRCS gradient_accumulator.cc
  DEPS blas
       operator
       lod_tensor
       selected_rows_utils
       selected_rows_functor
       var_type_traits
       layer
       math_function
       phi_tensor
       ${MLU_DEPS})
