from typing import Dict, List, Any, Optional
from hardware_profiler import HardwareProfiler
from model_database import ModelDatabase

class RecommendationEngine:
    def __init__(self):
        self.profiler = HardwareProfiler()
        self.db = ModelDatabase()
        self.hardware = self.profiler.get_summary()

    def _assess_use_cases(self, model: dict) -> dict:
        tags = [t.lower() for t in model.get('tags', [])]
        name = model.get('name', '').lower()
        desc = model.get('description', '').lower()
        ctx = str(model.get('context', ''))

        is_coder = 'coder' in name or 'code' in name or 'codificación' in tags
        is_reasoning = 'razonamiento' in tags or 'reason' in desc

        large_ctx = False
        try:
            if 'K' in ctx:
                ctx_k = int(ctx.replace('K', '').strip())
                large_ctx = ctx_k >= 32
        except:
            pass

        technical = is_coder or is_reasoning or large_ctx

        vision_keywords = ['vision', 'visual', 'image', 'llava', 'cogvlm', 'qwen-vl', 'gemini', 'multimodal']
        vision = any(kw in name for kw in vision_keywords) or 'vision' in tags or 'multimodal' in tags

        audio_keywords = ['whisper', 'bark', 'speech', 'voice', 'tts', 'stt', 'audio', 'music', 'sound', 'wav2vec', 'hubert', 'encodec', 'musicgen', 'audiogen', 'speaker', 'silero', 'coqui', 'text-to-speech', 'speech-to-text', 'speech-recognition']
        audio = any(kw in name for kw in audio_keywords) or any(kw in tags for kw in ['audio', 'speech', 'voice']) or 'audio' in desc or 'speech' in desc

        return {
            'technical': {
                'suitable': technical,
                'reason': 'Especializado en código y razonamiento técnico' if is_coder
                    else 'Gran contexto para prompts extensos' if large_ctx
                    else 'Capacidad general para tareas técnicas' if technical
                    else 'No ideal para tareas técnicas complejas'
            },
            'vision': {
                'suitable': vision,
                'reason': 'Soporta procesamiento de imágenes' if vision
                    else 'Solo texto, no procesa imágenes'
            },
            'audio': {
                'suitable': audio,
                'reason': 'Soporta procesamiento de audio/voz' if audio
                    else 'Solo texto, no procesa audio'
            }
        }

    def evaluate_models(self) -> List[Dict[str, Any]]:
        models = self.db.get_all_models()
        results = []
        for model in models:
            compatibility = self.db.check_compatibility(model['name'], self.hardware)
            use_cases = self._assess_use_cases(model)
            results.append({
                'model': model,
                'compatibility': compatibility,
                'use_cases': use_cases
            })
        return results

    def get_compatible_models(self) -> List[Dict[str, Any]]:
        return [r for r in self.evaluate_models() if r['compatibility']['compatible']]

    def get_recommendations(self, top_n: int = 5) -> List[Dict[str, Any]]:
        compatible = self.get_compatible_models()
        compatible.sort(key=lambda x: (
            -len(x['compatibility']['compatible_precisions']),
            x['compatibility']['compatible_precisions'][0]['memory_needed']
        ) if x['compatibility']['compatible_precisions'] else (0, 0))
        return compatible[:top_n]

    def generate_report(self) -> str:
        report = "\n" + "=" * 60 + "\n"
        report += "         RECOMENDACIÓN DE MOTORES DE IA\n"
        report += "=" * 60 + "\n\n"
        report += "HARDWARE DETECTADO:\n"
        report += "-" * 40 + "\n"
        report += f"RAM: {self.hardware['ram_gb']:.1f} GB\n"
        report += f"VRAM: {self.hardware['vram_gb']:.1f} GB\n"
        report += f"Disco: {self.hardware['disk_gb']:.1f} GB\n"
        report += f"GPU: {self.hardware['gpu_model']}\n\n"
        report += "MODELOS COMPATIBLES:\n"
        report += "-" * 40 + "\n"
        compatibles = self.get_compatible_models()
        if not compatibles:
            report += "No se encontraron modelos compatibles.\n"
        else:
            for i, r in enumerate(compatibles[:5], 1):
                model = r['model']
                comp = r['compatibility']
                best = comp['compatible_precisions'][0]
                uc = r['use_cases']
                report += f"\n{i}. {model['name']} ({model['params']}):\n"
                report += f"   Precision: {best['precision']} | RAM: {best['ram_needed']:.1f} GB | VRAM: {best['vram_needed']:.1f} GB\n"
                report += f"   Tecnica: {'Si' if uc['technical']['suitable'] else 'No'} | Vision: {'Si' if uc['vision']['suitable'] else 'No'} | Audio: {'Si' if uc['audio']['suitable'] else 'No'}\n"
        report += "\n" + "=" * 60 + "\n"
        return report
