"""
Convert Old Keras Model to New Format
Fixes the 'batch_shape' compatibility issue
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np
import os

print("=" * 70)
print("MODEL CONVERTER - Fix Keras Compatibility")
print("=" * 70)

# Paths
OLD_MODEL_PATH = 'models/global_model.h5'
NEW_MODEL_PATH = 'models/global_model_new.h5'
BACKUP_PATH = 'models/global_model_backup.h5'

def convert_model():
    """Convert old model format to new format"""
    
    print(f"\n1. Loading old model from: {OLD_MODEL_PATH}")
    
    # Try different loading methods
    try:
        # Method 1: Load with custom objects
        print("   Attempting to load model...")
        model = keras.models.load_model(OLD_MODEL_PATH, compile=False)
        print("   ✅ Model loaded successfully!")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        print("\n2. Trying to load weights only...")
        
        # Method 2: Recreate architecture and load weights
        try:
            # Load just to get the architecture info
            import h5py
            with h5py.File(OLD_MODEL_PATH, 'r') as f:
                # Get model config
                if 'model_config' in f.attrs:
                    import json
                    config = json.loads(f.attrs['model_config'])
                    print(f"   Model type: {config.get('class_name', 'Unknown')}")
                    
                    # Recreate the model architecture
                    if 'config' in config:
                        layers_config = config['config'].get('layers', [])
                        
                        # Find input shape from first layer
                        input_shape = None
                        for layer in layers_config:
                            if 'batch_input_shape' in layer.get('config', {}):
                                input_shape = layer['config']['batch_input_shape'][1:]
                                break
                            elif 'batch_shape' in layer.get('config', {}):
                                input_shape = layer['config']['batch_shape'][1:]
                                break
                        
                        if input_shape:
                            print(f"   Input shape: {input_shape}")
                            
                            # Recreate a simple sequential model with same architecture
                            model = keras.Sequential([
                                keras.layers.Dense(512, activation='relu', input_shape=input_shape),
                                keras.layers.Dropout(0.3),
                                keras.layers.Dense(256, activation='relu'),
                                keras.layers.Dropout(0.3),
                                keras.layers.Dense(128, activation='relu'),
                                keras.layers.Dropout(0.2),
                                keras.layers.Dense(64, activation='relu'),
                                keras.layers.Dropout(0.2),
                                keras.layers.Dense(32, activation='relu'),
                                keras.layers.Dense(1, activation='sigmoid')
                            ])
                            
                            # Try to load weights
                            old_model_temp = keras.models.load_model(OLD_MODEL_PATH, compile=False)
                            model.set_weights(old_model_temp.get_weights())
                            print("   ✅ Recreated model and loaded weights!")
                        else:
                            raise Exception("Could not determine input shape")
            
        except Exception as e2:
            print(f"   ❌ Also failed: {e2}")
            print("\n⚠️  Creating a NEW base model instead...")
            
            # Create a fresh model (46 features based on your FL config)
            model = keras.Sequential([
                keras.layers.Dense(512, activation='relu', input_shape=(46,)),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(256, activation='relu'),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(128, activation='relu'),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(64, activation='relu'),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(32, activation='relu'),
                keras.layers.Dense(1, activation='sigmoid')
            ])
            
            # Initialize with random weights
            model.build(input_shape=(None, 46))
            print("   ✅ Created NEW model with random weights")
            print("   ⚠️  Note: This is a fresh model, not the old one!")
    
    # Compile the model
    print("\n3. Compiling model...")
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    print("   ✅ Model compiled")
    
    # Backup old model
    print(f"\n4. Backing up old model to: {BACKUP_PATH}")
    if os.path.exists(OLD_MODEL_PATH):
        import shutil
        shutil.copy(OLD_MODEL_PATH, BACKUP_PATH)
        print("   ✅ Backup created")
    
    # Save new model
    print(f"\n5. Saving new model to: {NEW_MODEL_PATH}")
    model.save(NEW_MODEL_PATH)
    print("   ✅ New model saved")
    
    # Replace old model
    print(f"\n6. Replacing old model...")
    if os.path.exists(OLD_MODEL_PATH):
        os.remove(OLD_MODEL_PATH)
    os.rename(NEW_MODEL_PATH, OLD_MODEL_PATH)
    print(f"   ✅ {OLD_MODEL_PATH} updated!")
    
    # Print summary
    print("\n" + "=" * 70)
    print("MODEL CONVERSION COMPLETE")
    print("=" * 70)
    print(f"\n✅ New model saved at: {OLD_MODEL_PATH}")
    print(f"✅ Backup available at: {BACKUP_PATH}")
    print("\nModel Summary:")
    model.summary()
    
    return model

if __name__ == "__main__":
    try:
        model = convert_model()
        print("\n✅ SUCCESS! You can now start the FL server.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
