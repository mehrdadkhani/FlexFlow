from flexflow.core import *
import numpy as np
from flexflow.keras.datasets import mnist

def next_batch(idx, x_train, input1, ffconfig):
  start = idx*ffconfig.get_batch_size()
  x_train_batch = x_train[start:start+ffconfig.get_batch_size(), :]
  print(x_train_batch.shape)
  
  input1.inline_map(ffconfig)
  input_array = input1.get_array(ffconfig, DataType.DT_FLOAT)
  print(input_array.shape)
  for i in range(0, ffconfig.get_batch_size()):
    for j in range(0, 784):
      input_array[i][j] = x_train_batch[i][j]
  input1.inline_unmap(ffconfig)
  
def next_batch_label(idx, x_train, input1, ffconfig):
  start = idx*ffconfig.get_batch_size()
  x_train_batch = x_train[start:start+ffconfig.get_batch_size(), :]
  print(x_train_batch.shape)
  
  input1.inline_map(ffconfig)
  input_array = input1.get_array(ffconfig, DataType.DT_INT32)
  print(input_array.shape)
  for i in range(0, ffconfig.get_batch_size()):
    for j in range(0, 1):
      input_array[i][j] = x_train_batch[i][j]
  input1.inline_unmap(ffconfig)
  

def top_level_task():
  alexnetconfig = NetConfig()
  ffconfig = FFConfig()
  ffconfig.parse_args()
  print("Python API batchSize(%d) workersPerNodes(%d) numNodes(%d)" %(ffconfig.get_batch_size(), ffconfig.get_workers_per_node(), ffconfig.get_num_nodes()))
  ffmodel = FFModel(ffconfig)
  
  dims1 = [ffconfig.get_batch_size(), 784]
  input1 = ffmodel.create_tensor(dims1, "", DataType.DT_FLOAT);
  
  dims_label = [ffconfig.get_batch_size(), 1]
  label = ffmodel.create_tensor(dims_label, "", DataType.DT_INT32);
  
  num_samples = 60000
  
  (x_train, y_train), (x_test, y_test) = mnist.load_data()
  
  print(x_train.shape)
  x_train = x_train.reshape(60000, 784)
  x_train = x_train.astype('float32')
  x_train /= 255
  y_train = y_train.astype('int32')
  y_train = np.reshape(y_train, (len(y_train), 1))
  print(x_train.shape[0], 'train samples')
  print(y_train.shape)
  
  next_batch(0, x_train, input1, ffconfig)
  next_batch_label(0, y_train, label, ffconfig)
  
  t2 = ffmodel.dense("dense1", input1, 512, ActiMode.AC_MODE_RELU)
  t3 = ffmodel.dense("dense1", t2, 512, ActiMode.AC_MODE_RELU)
  t4 = ffmodel.dense("dense1", t3, 10)
  t5 = ffmodel.softmax("softmax", t4, label)

  ffoptimizer = SGDOptimizer(ffmodel, 0.01)
  ffmodel.set_sgd_optimizer(ffoptimizer)

  ffmodel.init_layers()

  epochs = ffconfig.get_epochs()
  ct = 0

  ts_start = ffconfig.get_current_time()
  for epoch in range(0,epochs):
    ffmodel.reset_metrics()
    iterations = num_samples / ffconfig.get_batch_size()
    for iter in range(0, 100):
      next_batch(ct, x_train, input1, ffconfig)
      next_batch_label(ct, y_train, label, ffconfig)      
      ct += 1
      if (epoch > 0):
        ffconfig.begin_trace(111)
      ffmodel.forward()
      ffmodel.zero_gradients()
      ffmodel.backward()
      ffmodel.update()
      if (epoch > 0):
        ffconfig.end_trace(111)

  ts_end = ffconfig.get_current_time()
  run_time = 1e-6 * (ts_end - ts_start);
  print("epochs %d, ELAPSED TIME = %.4fs, THROUGHPUT = %.2f samples/s\n" %(epochs, run_time, num_samples * epochs / run_time));
 #
  dense1 = ffmodel.get_layer_by_id(0)

  dbias_tensor = label#dense1.get_bias_tensor()
  dbias_tensor.inline_map(ffconfig)
  dbias = dbias_tensor.get_array(ffconfig, DataType.DT_INT32)
  print(dbias.shape)
  print(dbias)
  dbias_tensor.inline_unmap(ffconfig)

  # dweight_tensor = dense1.get_output_tensor()
  # dweight_tensor.inline_map(ffconfig)
  # dweight = dweight_tensor.get_array(ffconfig, DataType.DT_FLOAT)
  # print(dweight.shape)
  # print(dweight)
  # dweight_tensor.inline_unmap(ffconfig)
  
  
if __name__ == "__main__":
  print("alexnet")
  top_level_task()
