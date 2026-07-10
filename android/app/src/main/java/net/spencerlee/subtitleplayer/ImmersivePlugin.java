package net.spencerlee.subtitleplayer;

import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Toggles Android immersive mode, hiding both the status bar and the navigation
 * bar. Used by the web layer's fullscreen button. The bars still reappear
 * transiently on an edge swipe, then auto-hide (sticky immersive).
 */
@CapacitorPlugin(name = "Immersive")
public class ImmersivePlugin extends Plugin {

    private void setBarsHidden(final boolean hidden) {
        getActivity().runOnUiThread(() -> {
            WindowInsetsControllerCompat controller = WindowCompat.getInsetsController(
                getActivity().getWindow(), getBridge().getWebView());
            controller.setSystemBarsBehavior(
                WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            if (hidden) {
                controller.hide(WindowInsetsCompat.Type.systemBars());
            } else {
                controller.show(WindowInsetsCompat.Type.systemBars());
            }
        });
    }

    @PluginMethod
    public void enable(PluginCall call) {
        setBarsHidden(true);
        call.resolve();
    }

    @PluginMethod
    public void disable(PluginCall call) {
        setBarsHidden(false);
        call.resolve();
    }
}
