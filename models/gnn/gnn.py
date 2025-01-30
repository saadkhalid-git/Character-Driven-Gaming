import torch
import torch.nn.functional as F
from torch.nn import Linear, ReLU, BatchNorm1d, Dropout
from torch_geometric.nn import GCNConv

class GNNRecommender(torch.nn.Module):
    def __init__(self, 
                 num_features:int,
                 hidden_channels:list,
                 classifier_hidden_dims:list,
                 use_dropout_in_conv:bool = True,
                 use_dropout_in_classifier:bool = True,
                 dropout_rate:float = 0.3,
                 use_input_masking:bool = True,
                 debug:bool = True):
        super(GNNRecommender, self).__init__()
        assert type(hidden_channels) in (list, tuple), "Expected a list or tuple for 'hidden_channels' arg" 

        self.debug = debug
        self.use_input_masking = use_input_masking
        self.use_dropout_in_classifier = use_dropout_in_classifier
        self.use_dropout_in_conv = use_dropout_in_conv
        self.dropout_rate = dropout_rate
        
        self.convs, self.conv_activations = self.build_conv_blocks(num_features, hidden_channels)
        self.classifier = self.build_classifier(hidden_channels[-1], classifier_hidden_dims)
        if use_input_masking:
            self.input_masking = Dropout(dropout_rate)

    def build_classifier(self, input_dim:int, hidden_dims:list):
        layers = []
        for hidden_dims_ in hidden_dims:
            layers.extend([
                Linear(input_dim, hidden_dims_)
            ])
            if self.use_dropout_in_classifier:
                layers.append(Dropout(self.dropout_rate))
            layers.append(ReLU())
            input_dim = hidden_dims_
        layers.append(Linear(input_dim, 1))
        return torch.nn.Sequential(*layers)

    def build_conv_blocks(self, input_channels:int, hidden_channels:list) -> tuple:
        convs = torch.nn.ModuleList()
        conv_activations = torch.nn.ModuleList()
        for hidden_channels_ in hidden_channels:
            convs.append(GCNConv(input_channels, hidden_channels_))
            conv_activation = [BatchNorm1d(hidden_channels_), ReLU()]
            if self.use_dropout_in_conv:
                conv_activation.append(Dropout(self.dropout_rate))
            conv_activations.append(torch.nn.Sequential(*conv_activation))
            input_channels = hidden_channels_
        return convs, conv_activations
        
    def forward(self, data, return_embeddings=False):
        """
        If return_embeddings=True, returns:
            node_embeddings (shape: [num_nodes, hidden_channels]), 
            final_predictions (shape: [num_nodes, 1])
        Otherwise, returns only the final_predictions.
        """
        x, edge_index = data.x, data.edge_index
        edge_attr = data.edge_attr  

        # -- GNN layers --
        if self.use_input_masking:
            x = self.input_masking(x)

        features_map = x
        for i in range(len(self.convs)):
            features_map = self.convs[i](features_map, edge_index)
            features_map = self.conv_activations[i](features_map)

        if self.debug:
            print(f"[DEBUG] Features map shape: {features_map.shape}")
        node_embeddings = features_map.clone()
        
        # -- Final MLP to get scalar predictions per node
        y = self.classifier(features_map)
        if self.debug:
            print(f"[DEBUG] Output shape: {y.shape}")
        
        if return_embeddings:
            return node_embeddings, y
        else:
            return y
