from abstract_network import *
import os


class Visualizer:
    def __init__(self, network):
        plt.ion()
        plt.show()
        self.fig = None
        self.network = network
        self.name = "default"
        self.save_epoch = 0
        self.array_save_epoch = 0

    def visualize(self, **args):
        pass

    def fig_to_file(self, fig=None):
        if fig is None:
            fig = self.fig
        img_folder = "models/" + self.network.name + "/" + self.name
        if not os.path.isdir(img_folder):
            os.makedirs(img_folder)

        fig_name = "current.png"
        fig.savefig(os.path.join(img_folder, fig_name))
        fig_name = "epoch%d" % self.save_epoch + ".png"
        fig.savefig(os.path.join(img_folder, fig_name))
        self.save_epoch += 1


class ConditionalSampleVisualizer(Visualizer):
    """ sess should be the session where the visualized network run,
    visualized_variable should be a [batch_size, *] tensor, and title is the title of plotted graph """
    def __init__(self, network, dataset):
        Visualizer.__init__(self, network)
        self.dataset = dataset
        self.name = "conditional_samples"

    def visualize(self, layers, num_rows=4):
        if self.fig is None:
            self.fig, self.ax = plt.subplots(1, len(layers))
        latent_code = self.network.random_latent_code()
        for i, layer in enumerate(layers):
            samples = np.zeros([num_rows*num_rows]+self.dataset.data_dims)
            samples_ptr = 0
            while samples_ptr < num_rows * num_rows:
                # Generate a few samples each time. Too many samples with distribution on latent code
                # different from training time breaks batch norm
                new_samples, _ = self.network.generate_conditional_samples(layer, latent_code)
                next_ptr = samples_ptr + new_samples.shape[0]
                if next_ptr > num_rows * num_rows:
                    next_ptr = num_rows * num_rows

                samples[samples_ptr:next_ptr] = new_samples[0:next_ptr-samples_ptr]
                samples_ptr = next_ptr

            # Plot the samples in a grid
            if samples is not None:
                samples = self.dataset.display(samples)
                width = samples.shape[1]
                height = samples.shape[2]
                channel = samples.shape[3]
                canvas = np.zeros((width * num_rows, height * num_rows, channel))
                for img_index1 in range(num_rows):
                    for img_index2 in range(num_rows):
                        canvas[img_index1 * width:(img_index1 + 1) * width,
                            img_index2 * height:(img_index2 + 1) * height, :] = \
                            samples[img_index1 * num_rows + img_index2, :, :, :]
                self.ax[i].cla()
                if channel == 1:
                    self.ax[i].imshow(canvas[:, :, 0], cmap=plt.get_cmap('Greys'))
                else:
                    self.ax[i].imshow(canvas)
                self.ax[i].xaxis.set_visible(False)
                self.ax[i].yaxis.set_visible(False)
            else:
                print("Warning: no samples generated during visualization")
        # np.save('samples', canvas)
        self.fig_to_file()
        self.fig.suptitle('Conditional Samples for %s' % self.network.name)
        plt.draw()
        plt.pause(0.01)


class SampleVisualizer(Visualizer):
    """ sess should be the session where the visualized network run,
    visualized_variable should be a [batch_size, *] tensor, and title is the title of plotted graph """
    def __init__(self, network, dataset):
        Visualizer.__init__(self, network)
        # self.fig.suptitle("Samples generated by " + str(network.name))
        self.dataset = dataset
        self.name = "samples"

    def visualize(self, num_rows=10):
        if self.fig is None:
            self.fig, self.ax = plt.subplots()
        samples = self.network.generate_samples()
        if samples is not None:
            samples = self.dataset.display(samples)
            width = samples.shape[1]
            height = samples.shape[2]
            channel = samples.shape[3]
            canvas = np.zeros((width * num_rows, height * num_rows, channel))
            for img_index1 in range(num_rows):
                for img_index2 in range(num_rows):
                    canvas[img_index1*width:(img_index1+1)*width, img_index2*height:(img_index2+1)*height, :] = \
                        samples[img_index1*num_rows+img_index2, :, :, :]
            self.ax.cla()
            if channel == 1:
                self.ax.imshow(canvas[:, :, 0], cmap=plt.get_cmap('Greys'))
            else:
                self.ax.imshow(canvas)
            self.ax.xaxis.set_visible(False)
            self.ax.yaxis.set_visible(False)

            # if not os.path.isdir('result_log/%s' % self.network.name):
            #     os.mkdir('result_log/%s' % self.network.name)
            # np.save('result_log/%s/samples%d' % (self.network.name, self.count), canvas)
            # np.save('result_log/%s/samples' % self.network.name, canvas)
            self.fig_to_file()
            self.fig.suptitle('Samples for %s' % self.network.name)
            plt.draw()
            plt.pause(0.01)


class ManifoldSampleVisualizer(Visualizer):
    def __init__(self, network, dataset):
        Visualizer.__init__(self, network)
        # self.fig.suptitle("Samples generated by " + str(network.name))
        self.dataset = dataset
        self.name = "manifold_samples"

    def visualize(self, layers, num_rows=4):
        if self.fig is None:
            self.fig, self.ax = plt.subplots(1, len(layers))
        for i, layer in enumerate(layers):
            samples = np.zeros([num_rows*num_rows]+self.dataset.data_dims)
            samples_ptr = 0
            latent_code_x = np.tile(np.reshape(np.linspace(-2.0, 2.0, num=num_rows), (1, num_rows)), (num_rows, 1))
            latent_code_y = latent_code_x.transpose()
            latent_code = np.reshape(np.stack([latent_code_x, latent_code_y], axis=-1), (-1, 2))
            while samples_ptr < num_rows * num_rows:
                new_samples = self.network.generate_manifold_samples(layer, latent_code)
                latent_code = latent_code[new_samples.shape[0]:]
                next_ptr = samples_ptr + new_samples.shape[0]
                if next_ptr > num_rows * num_rows:
                    next_ptr = num_rows * num_rows

                samples[samples_ptr:next_ptr] = new_samples[0:next_ptr-samples_ptr]
                samples_ptr = next_ptr
            if samples is not None:
                width = samples.shape[1]
                height = samples.shape[2]
                channel = samples.shape[3]
                canvas = np.zeros((width * num_rows, height * num_rows, channel))
                for img_index1 in range(num_rows):
                    for img_index2 in range(num_rows):
                        canvas[img_index1 * width:(img_index1 + 1) * width,
                        img_index2 * height:(img_index2 + 1) * height, :] = \
                            self.dataset.display(samples[img_index1 * num_rows + img_index2, :, :, :])
                self.ax[i].cla()
                if channel == 1:
                    self.ax[i].imshow(canvas[:, :, 0], cmap=plt.get_cmap('Greys'))
                else:
                    self.ax[i].imshow(canvas)
                self.ax[i].xaxis.set_visible(False)
                self.ax[i].yaxis.set_visible(False)
        self.fig_to_file()
        self.fig.suptitle('Manifold Samples for %s' % self.network.name)
        plt.draw()
        plt.pause(0.01)

