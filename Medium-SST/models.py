import torch
import torch.nn as nn
import torch.nn.functional as F


class LSTM(nn.Module):
    def __init__(self, config):
        super(RNN, self).__init__()
        self.rnn = nn.LSTM(
            input_size=config.input_size, hidden_size=config.hidden_size,
            num_layers=config.num_layers, bidirectional=config.bidirectional,
            batch_first=config.batch_first)
        self.init_params()
        self.dropout = nn.Dropout(p=config.dropout)

    def init_params(self):
        for i in range(self.rnn.num_layers):
            nn.init.orthogonal_(getattr(self.rnn, f'weight_hh_l{i}'))
            nn.init.kaiming_normal_(getattr(self.rnn, f'weight_ih_l{i}'))
            nn.init.constant_(getattr(self.rnn, f'bias_hh_l{i}'), val=0)
            nn.init.constant_(getattr(self.rnn, f'bias_ih_l{i}'), val=0)
            getattr(self.rnn, f'bias_hh_l{i}').chunk(4)[1].fill_(1)

            if self.rnn.bidirectional:
                nn.init.orthogonal_(
                    getattr(self.rnn, f'weight_hh_l{i}_reverse'))
                nn.init.kaiming_normal_(
                    getattr(self.rnn, f'weight_ih_l{i}_reverse'))
                nn.init.constant_(
                    getattr(self.rnn, f'bias_hh_l{i}_reverse'), val=0)
                nn.init.constant_(
                    getattr(self.rnn, f'bias_ih_l{i}_reverse'), val=0)
                getattr(self.rnn, f'bias_hh_l{i}_reverse').chunk(4)[1].fill_(1)


class Conv(nn.Module):
    def __init__(self, in_channels, out_channels, filter_sizes):
        super(Conv, self).__init__()
        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=in_channels,
                      out_channels=out_channels,
                      kernel_size=fs)
            for fs in filter_sizes
        ])

    def init_params(self):
        for m in self.convs:
            nn.init.xavier_uniform(m.weight.data)
            nn.init.constant(m.bias.data, 0.1)

    def forward(self, x):
        return [F.relu(conv(x)) for conv in self.convs]


class Linear(nn.Module):
    def __init__(self, in_features, out_features):
        super(Linear, self).__init__()

        self.linear = nn.Linear(in_features=in_features,
                                out_features=out_features)
        self.init_params()

    def init_params(self):
        nn.init.kaiming_normal_(self.linear.weight)
        nn.init.constant_(self.linear.bias, 0)

    def forward(self, x):
        x = self.linear(x)
        return x